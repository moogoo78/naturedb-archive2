(function() {

  const TERM_LABELS = {
    field_number: '採集號',
    field_number_range: '採集號範圍',
    collector: '採集者',
    taxon: '學名',
    named_area: '地點',
    accession_number: '館號',
    };

  const searchInput = document.getElementById('phok-searchbar');
  const choiceList = document.getElementById('phok-choice-list');
  const tokenContainer = document.getElementById('phok-tokens-container');
  const submitButton = document.getElementById('phok-submit');
  const printButton = document.getElementById('phok-print');
  const printClearButton = document.getElementById('phok-print-clear');
  const resultsTBody = document.getElementById('phok-results-tbody');
  const resultsContainer = document.getElementById('phok-results-container');
  const resultsLoading = document.getElementById('phok-results-loading');
  let storeRecordsSet = null;

  const parseItem = (item) => {
    let text = '';
    let value = null;
    if (item.term === 'accession_number') {
      text = `HAST: ${item.accession_number}`;
      value = item.accession_number;
    } else if (item.term === 'field_number') {
      text = `${item.collector.display_name} ${item.field_number}`;
      value = `collector::${item.collector.id}||field_number::${item.field_number}`;
    } else if (item.term === 'taxon') {
      text = `${item.full_scientific_name} ${item.common_name}`;
      value = '';
    } else {
      text = item.display_name;
      value = item.id || '';
    }
    return {
      term: item.term,
      label: TERM_LABELS[item.term],
      text: text,
      value: value,
    }
  };

  const renderFilterToken = (item) => {
    //console.log(data);
    let token = document.createElement('div');
    const d = parseItem(item);
    token.innerHTML = `<a class="uk-alert-close" uk-close></a><p><span class="uk-label uk-label-success">${d.label}</span> = <span class="uk-text-small">${d.text}</span></p>`;
    token.setAttribute('uk-alert', '');
    token.classList.add('phok-token', 'uk-border-rounded', 'uk-background-default');
    token.dataset.term = d.term;
    token.dataset.value = d.value;
    tokenContainer.appendChild(token);
  };

  const renderChoices = (data) => {
    // clear
    choiceList.innerHTML = '';

    const handleClick = (e) => {
      // not work!?
      //e.preventDefault();
      //e.stopPropagation();
      //e.stopImmediatePropagation();
      //console.log(e.target, e.currentTarget);
      const selectedIndex = e.currentTarget.dataset['key'];
      UIkit.dropdown('#phok-choice-menu').hide(false);
      renderFilterToken(data[selectedIndex]);
      searchInput.value = '';
    }

    data.forEach((item, index) => {
      const { label, text } = parseItem(item);
      let choice = document.createElement('li');
      choice.addEventListener('click', handleClick, true);
      choice.dataset.key = index;
      //const choiceFlex = document.createElement('div');
      const choiceFlexLeft = document.createElement('div');
      const choiceFlexRight = document.createElement('div');
      const textTitle = document.createTextNode(text);
      const textTerm = document.createTextNode(label);
      choice.classList.add('phok-choice-item');
      choice.classList.add('uk-flex', 'uk-flex-between');
      choiceFlexLeft.classList.add('uk-padding-small', 'uk-padding-remove-vertical');
      choiceFlexRight.classList.add('uk-padding-small', 'uk-padding-remove-vertical' ,'uk-text-muted');
      choiceFlexLeft.appendChild(textTitle);
      choiceFlexRight.appendChild(textTerm);
      choice.append(choiceFlexLeft);
      choice.append(choiceFlexRight);
      //choice.append(choiceFlex);
      choiceList.appendChild(choice);

      /* return `<li class="phok-suggestion-item">
         <div class="uk-flex uk-flex-between">
       *   <div class="uk-padding-small uk-padding-remove-vertical">${text}</div>
       *   <div class="uk-padding-small uk-padding-remove-vertical uk-text-muted">${TERM_LABELS[item.term]}</div>
         </div>
         </li>`; */
    });
  }

  const renderResults = (results) => {
    resultsTBody.innerHTML = '';

    const renderDetailLink = (content, collectionId) => {
      return `<a class="uk-link-reset" href="/admin/collections/${collectionId}">${content}</a>`;
    };

    results.data.forEach(item => {
      let scientificName = '';
      let commonName = '';
      if (item.taxon_text) {
        const nameList = item.taxon_text.split('|');
        if (nameList.length > 1) {
          scientificName = nameList[0];
          commonName = nameList[1];
        }
      }
      const namedAreas = item.named_areas.map(x => x.name);

      const row = document.createElement('tr');
      let col1 = document.createElement('td');
      let chk = document.createElement('input');
      chk.type = 'checkbox';
      chk.classList.add('uk-checkbox');
      if (storeRecordsSet.has(item.record_key)) {
        chk.checked = true;
      }
      chk.onchange = (e) => {
        //console.log(e, e.target.value, e.target.checked, e.currentTarget.value, item.record_key);
        if (storeRecordsSet.has(item.record_key)) {
          storeRecordsSet.delete(item.record_key)
        } else {
          storeRecordsSet.add(item.record_key);
        }
        localStorage.setItem('store-records', JSON.stringify(Array.from(storeRecordsSet)));
        printButton.innerHTML = `Print (${storeRecordsSet.size})`;
      }
      col1.appendChild(chk);
      let col2 = document.createElement('td');
      col2.classList.add('uk-table-link');
      let tmp = (item.image_url) ? `<img class="uk-preserve-width uk-border-rounded" src="${item.image_url}" width="40" height="40" alt="">` : '';
      col2.innerHTML = renderDetailLink(tmp, item.collection_id);
      let col3 = document.createElement('td');
      col3.classList.add('uk-table-link');
      tmp = item.accession_number || '';
      col3.innerHTML = renderDetailLink(tmp, item.collection_id);
      let col4 = document.createElement('td');
      col4.classList.add('uk-table-link');
      tmp = `${scientificName} ${commonName}`;
      col4.innerHTML = renderDetailLink(tmp, item.collection_id);
      let col5 = document.createElement('td');
      col5.classList.add('uk-table-link');
      tmp = (item.collector) ? `${item.collector.display_name} <span class="uk-text-bold">${item.field_number}</span>` : `<span class="uk-text-bold">${item.field_number}</span>`;
      col5.innerHTML = renderDetailLink(tmp, item.collection_id);
      let col6 = document.createElement('td');
      tmp = item.collect_date;
      col6.innerHTML = renderDetailLink(tmp, item.collection_id);
      col6.classList.add('uk-table-link');
      let col7 = document.createElement('td');
      col7.innerHTML = namedAreas.join('/');
      col7.classList.add('uk-table-link');
      row.appendChild(col1);
      row.appendChild(col2);
      row.appendChild(col3);
      row.appendChild(col4);
      row.appendChild(col5);
      row.appendChild(col6);
      row.appendChild(col7);
      resultsTBody.appendChild(row);
    });



  };

  const onSearchbar = (e) => {
    const q = e.target.value;
    const endpoint = `/api/v1/searchbar?q=${q}`;
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
        renderChoices(json.data);
      })
      .catch(error => console.log(error));
  }

  searchInput.addEventListener('input', onSearchbar);

  submitButton.onclick = (e) => {
    resultsContainer.setAttribute('hidden', '');
    resultsLoading.removeAttribute('hidden');

    const tokens = document.querySelectorAll('.phok-token');
    const payload = {};
    const filter = {};
    tokens.forEach((x) => {
      if( x.dataset.term === 'field_number') {
        const vlist = x.dataset.value.split('||');
        vlist.forEach( v => {
          const tlist = v.split('::');
          if (tlist[0] === 'collector') {
            filter[tlist[0]] = [tlist[1]]; // HACK
          } else {
            filter[tlist[0]] = tlist[1];
          }
        });
      } else if (x.dataset.term === 'collector') {
        filter[x.dataset.term] = [x.dataset.value]; //HACK
      }else {
        filter[x.dataset.term] = x.dataset.value;
      }
    });

    payload['filter'] = JSON.stringify(filter);
    console.log(payload, filter);
    const queryString = new URLSearchParams(payload).toString()
    const seperator = (queryString === '') ? '' : '?';
    const url = `/api/v1/explore${seperator}${queryString}`;
    const headers = {
      "Accept": "application/json",
      "Content-Type": "application/json; charset=utf-8",
      'X-Requested-With': 'XMLHttpRequest'
    };

    fetch(url, {
      method: "GET",
      cache: "no-cache",
      credentials: "same-origin",
      headers: headers,
    })
      .then(response => response.json())
      .then(json => {
        //console.log(json);
        renderResults(json);
        resultsContainer.removeAttribute('hidden');
        resultsLoading.setAttribute('hidden', '');
      })
      .catch(error => console.log(error));
    ;
  };

  printButton.onclick = () => {
    window.open(`/print-label?keys=${Array.from(storeRecordsSet).join(',')}`, '_blank');
  }
  printClearButton.onclick = () => {
    localStorage.removeItem('store-records');
    storeRecordsSet = new Set();
    printButton.innerHTML = `Print`;
  }

  const init = () => {
    const storeRecords = localStorage.getItem('store-records');
    if (storeRecords) {
    const values = JSON.parse(storeRecords);
      storeRecordsSet = new Set(values);
      printButton.innerHTML = `Print (${storeRecordsSet.size})`;
    } else {
      storeRecordsSet = new Set();
    }
  };

  init();
  //console.log('store records', storeRecordsSet);
})();
