
/*
ret.forEach(el => console.log(el.textContent));

var x = ret.at(-5)
*/

function get_all_time_frames(root) {
    if (!root) return [];

    const ret = [];

    // Find all elements containing GTEM text
    const allNodes = Array.from(root.querySelectorAll('*'));
    const unfiltered_parents = [];
    for (let el of allNodes) {
        // 2 - for GTC, Day
        // 4- all 
        if (el.textContent && el.textContent.includes('GTC') && el.children.length > 1 && el.children.length < 5) {
            unfiltered_parents.push(el);
        }
    }

    const filtered_parents = unfiltered_parents.filter(el =>
        Array.from(el.children).some(child =>
            child.classList.contains('q-dropmenu-option')
        )
    );
    if (filtered_parents.length == 1) {
        ret.push(...Array.from(filtered_parents[0].children).map(child => child.textContent))
    }


    // Pierce Shadow DOM
    for (let child of root.querySelectorAll('*')) {
        if (child.shadowRoot) {
            ret.push(...get_all_time_frames(child.shadowRoot));
        }
    }
    return ret;
}
return get_all_time_frames(document);