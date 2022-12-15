import { fetchData } from './utils.js'

(function() {

  const form = document.getElementById('main-form');
  const formData = new FormData(form);
  const makeLocation = (namedAreas) => {
    namedAreas.forEach((x)=> {
      /*
      const itemWrapper = document.createElement('div');
      let item = document.createElement('div');
      let label = document.createElement('label');
      let ctrl = document.createElement('div');
      let ctrl = document.createElement('input');
      */
    });
  }

  const makeCollector = (data) => {
    //const collectorListContainer = document.getElementById('collector-list-container');
    const collectorList = document.getElementById('collector-list');
    //collectorListContainer.innerHTML = '';
    collectorList.innerHTML = '';
    data.forEach((item, index) => {
      let choice = document.createElement('li');
      choice.addEventListener('click', (e) => {
        e.preventDefault();
        e.stopPropagation();
        console.log(e.currentTarget);
        const selectedIndex = e.currentTarget.dataset['key'];
        //console.log(data[selectedIndex]);
        UIkit.dropdown('#collector-list-container').hide(false);
        form.collector.value = data[selectedIndex].display_name;
        form.collector.dataset.realid = data[selectedIndex].id;
      }, true);
      choice.dataset.key = index;
      choice.innerHTML = `<a href="#">${item.display_name}</a>`;
      collectorList.appendChild(choice);
    });
    // TODO: uk-form-danger not select
  }

  const makeForm = ({data, formOptions}) => {
    //console.log(data, formOptions);

    form.collector.addEventListener('input', (e) => {
      const filter = {
        q: e.target.value,
      }
      const endpoint = `/api/v1/people?filter=${JSON.stringify(filter)}`;
      fetchData(endpoint).then( results => {
        makeCollector(results.data);
      });

    });
    form.field_number.value = data.field_number;
    form.collect_date.value = data.collect_date;
    form.companion_text.value = data.companion_text;
    form.companion_text_en.value = data.companion_text_en;
    makeLocation(formOptions.named_areas);
  }

  const init = () => {

    /*
    console.log(formData);

    for (const [key, value] of formData) {
      console.log(`${key}: ${value}`);
    }
    formData.set('kaka', 'bbb');

    for (const [key, value] of formData) {
      console.log(`${key}: ${value}`);
    }
    form.elements.kaka.value= 'uu';
    */

    // fetch data
    const re = /(\/admin\/collections\/)(?<itemId>[0-9]+)/;
    const collectionId = window.location.pathname.match(re).groups.itemId;
    const endpoint = `/api/v1/collections/${collectionId}`;
    const headers = {
      "Accept": "application/json",
      "Content-Type": "application/json; charset=utf-8",
      'X-Requested-With': 'XMLHttpRequest'
    };
    fetch(endpoint, {
      method: "GET",
      cache: "no-cache",
      credentials: "same-origin",
      headers: headers,
    })
      .then(response => response.json())
      .then(json => {
        makeForm({data: json.data, formOptions: json.form});
      })
      .catch(error => console.log(error));
  };

  init();
})();
