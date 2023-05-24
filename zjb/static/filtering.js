function filter_rows() {
    let query = document.getElementById('search').value.toLowerCase();
    let rows = document.querySelectorAll(
        'table.view > tbody > tr, table.notes > tbody > tr'
    );

    for(const row of rows) {
        if(query == '' || row.dataset['search'].toLowerCase().match(query)) {
            row.style.display = '';
        } else {
            row.style.display = 'none';
        }
    }
}

function update_URL() {
    if(window.history.replaceState) {
        let query = document.getElementById('search').value.toLowerCase();
        let url = window.location.origin + window.location.pathname;

        if(query) {
            url += '?q=' + query;
        }

        window.history.replaceState({}, '', url);
    }
}

function bind_search_elements() {
    let group_select = document.getElementById('group');
    if(group_select) {
        for(const group in GROUPS) {
            const option = document.createElement('option');
            const text = document.createTextNode(group);
            option.appendChild(text);
            group_select.appendChild(option);
        }

        group_select.addEventListener('change', function(event) {
            filter_rows();
        });
    }

    let input_search = document.getElementById('search');
    if(input_search) {
        input_search.addEventListener('input', function(event) {
            filter_rows();
            update_URL();
        });

        if(input_search.value) {
            filter_rows();
            update_URL();
        }
    }

    let button_failed = document.getElementById('failed');
    if(button_failed) {
        button_failed.addEventListener('click', function(event) {
            let input_search = document.getElementById('search');
            if(input_search) {
                input_search.value = '(FAILURE|RETRY|ABORT)';
                filter_rows();
                update_URL();
            }
        });
    }

    let button_tested = document.getElementById('tested');
    if(button_tested) {
        button_tested.addEventListener('click', function(event) {
            let input_search = document.getElementById('search');
            if(input_search) {
                input_search.value = '(SUCCESS|FAILURE|RETRY|ABORT)';
                filter_rows();
                update_URL();
            }
        });
    }

    let button_untested = document.getElementById('untested');
    if(button_untested) {
        button_untested.addEventListener('click', function(event) {
            let input_search = document.getElementById('search');
            if(input_search) {
                input_search.value = '^((?!(SUCCESS|FAILURE|RETRY|ABORT)).)*$';
                filter_rows();
                update_URL();
            }
        });
    }
}
