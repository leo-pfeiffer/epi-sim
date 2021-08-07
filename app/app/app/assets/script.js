/**
 * General custom javascript to customise the app.
 * */

/*
* Due to a bug in Plotly (https://github.com/plotly/plotly.js/issues/4155),
* an error is thrown when the space required for a heatmap is too small.
* This would prevent the page from being loaded in some cases.
* As a way around it, the Heatmap is hidden if the space is not sufficient and
* the user is asked to resize the window. Upon resizing the window, the Heatmap
* is initially too large for the Div. To trigger a rerender, this function
* triggers another click on the active tab to force the figure to be rendered
* inside the bounds of the Div, fixing the issue.
* */
function heatmapResize () {

    // only do this if we're on the index page
    const pathname = document.location.pathname
    if (pathname !== "/" && pathname !== "") {
        return;
    }

    // get all tabs
    const tabs = document.getElementById('heatmap-card-tabs').children

    // get the active tab and one inactive tab
    let activeTab;
    let inActiveTab;
    for (let t of tabs) {
        if (t.firstElementChild.classList.contains('active')) {
            activeTab = t
        } else {
           inActiveTab = t
        }
        if (activeTab !== undefined && inActiveTab !== undefined) {
            break
        }
    }

    // make sure we actually found the elements
    if (activeTab !== undefined && inActiveTab !== undefined) {

        // trigger a reload of another element...
        inActiveTab.firstElementChild.click()

        // ... immediately followed by a reload of the original element.
        activeTab.firstElementChild.click()
    }
}

// EVENT LISTENERS
window.addEventListener('resize', heatmapResize);