import {
  fetchData,
  getRandString,
} from '../utils.js'

(function() {
  "use strict";

  let allAutocompletes = document.querySelectorAll('input[sh-autocomplete]');
  allAutocompletes.forEach( x => {
    console.log(x);
  });

  const myListbox = (() => {
    'use strict';
    const wrapper = function () {
      let pub = {};
      let queryUrlPrefix = null;
      const state = {
        input: null,
        dropdown: null,
        dropdownList: [],
      };
      const conf = {
        inputId: '',
        dropdownId: '',
      };

      pub.on = ((inputId, urlPrefix) => {
        conf.inputId = inputId;
        state.input = document.getElementById(conf.inputId);
        state.input.addEventListener('input', handleInput)
        queryUrlPrefix = urlPrefix;

        const rand = getRandString(4);
        conf.dropdownId = `de-${conf.inputId}__dropdown-${rand}`;
        // create DOM
        state.dropdown = document.createElement('div');
        state.dropdown.className = 'uk-width-1-2 uk-margin-remove';
        state.dropdown.setAttribute('uk-dropdown', `mode: click; pos: bottom-justify; boundary: !.${conf.inputId}; auto-update: false`);
        state.dropdown.setAttribute('id', conf.dropdownId);
        state.dropdownList = document.createElement('ul');
        state.dropdownList.className = 'uk-list uk-list-divider uk-padding-remove-vertical'
        state.input.insertAdjacentElement('afterend', state.dropdown);
        state.dropdown.appendChild(state.dropdownList);
      });

      const renderList = data => {
        state.dropdownList.innerHTML = '';
        console.log(data);
        data.forEach( (d, index) => {
          let item = document.createElement('li');

          //item.addEventListener('click', handleChoiceClick, true);
          item.dataset.key = index;
          item.classList.add('uk-flex', 'uk-flex-between');
          item.innerHTML = `
            <div class="uk-padding-small uk-padding-remove-vertical">${d.display_name}</div>
            <div class="uk-padding-small uk-padding-remove-vertical uk-text-muted"></div>`;
          state.dropdownList.appendChild(item);
        });
      }

      const handleInput = (e) => {
        if (e.target.value) {
          const filter = { q: e.target.value };
          const payload = {
            filter: JSON.stringify(filter),
          }

          const queryString = new URLSearchParams(payload).toString()
          const endpoint = `${queryUrlPrefix}?${queryString}`;
          fetchData(endpoint)
            .then( resp => {
              //renderChoices(resp.data);
              renderList(resp.data);
            })
            .catch( error => {
              console.log(error);
            });
        } else {
          //UIkit.dropdown(`#${conf.dropdownId}`).hide(false);
        }
      }
      return pub;
    }
    return wrapper;
  })();


  let lb1 = new myListbox()
  lb1.on('collector-input', '/api/v1/people');
})();
