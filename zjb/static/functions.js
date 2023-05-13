function set_tables_widths() {
    let tables = document.querySelectorAll('table.view');
    for(const table of tables) {
        table.width = table.offsetWidth;
    }
}

function toggle_table_visibility(event) {
    let elements = event.currentTarget.parentElement.querySelectorAll(
        'table.view > tbody, table.view > thead, table.view > tfoot'
    );
    for(const element of elements) {
        element.hidden = ! element.hidden;
    }
}

function make_tables_collapsible() {
    let captions = document.querySelectorAll('table.view > caption');
    for(const caption of captions) {
        caption.addEventListener('click', toggle_table_visibility);
    }
}

function on_page_load(event) {
    set_tables_widths();
    make_tables_collapsible();
    bind_search_elements();
    bind_links_to_overlays();
    bind_events_to_forms();
}

document.addEventListener('DOMContentLoaded', on_page_load);
