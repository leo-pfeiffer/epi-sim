/*
* Contains dash client side callbacks.
* */

/**
 * Add a new style sheet to the DOM.
 * */
const addStyleSheet = function(url) {
    const link = document.createElement('link')
    link.href = url
    link.rel = 'stylesheet'

    const head = document.querySelector('head')
    head.appendChild(link)
}


window.dash_clientside = Object.assign({}, window.dash_clientside, {
    clientside: {

        /**
         * Switch between stylesheet when routing occurs.
         * */
        switchStylesheetCallback: function(url) {

            // selector strings
            const INDEX_SELECTOR = 'link[rel=stylesheet][href^="/assets/index-page.css"]'
            const TEXT_SELECTOR = 'link[rel=stylesheet][href^="/assets/text-page.css"]'
            const VALIDATION_SELECTOR = 'link[rel=stylesheet][href^="/assets/validation-page.css"]'

            // CSS urls
            const INDEX_CSS = '/assets/index-page.css'
            const TEXT_CSS = '/assets/text-page.css'
            const VALIDATION_CSS = '/assets/validation-page.css'

            // Map stylesheets to URLs
            const STYLESHEETS = {
                '/': {
                    selector: INDEX_SELECTOR,
                    css: INDEX_CSS
                },
                '/models': {
                    selector: TEXT_SELECTOR,
                    css: TEXT_CSS
                },
                '/networks': {
                    selector: TEXT_SELECTOR,
                    css: TEXT_CSS
                },
                '/about': {
                    selector: TEXT_SELECTOR,
                    css: TEXT_CSS
                },
                '/validation': {
                    selector: VALIDATION_SELECTOR,
                    css: VALIDATION_CSS
                },
                '/not-found': {
                    selector: TEXT_SELECTOR,
                    css: TEXT_CSS
                }
            }

            // in case the url doesn't exist
            if (!STYLESHEETS.hasOwnProperty(url)) {

                url = '/not-found'
            }

            // query the target sheet
            const node = document.querySelector(STYLESHEETS[url]['selector']);

            // add stylesheet if it isn't already there
            if (node === null) {
                addStyleSheet(STYLESHEETS[url]['css'])
            }

            // remove other stylesheets
            for (let u of Object.keys(STYLESHEETS)) {
                const sheet = STYLESHEETS[u]

                // don't remove the currently needed sheet
                if (u !== url && sheet['css'] !== STYLESHEETS[url]['css']) {

                    // the sheet we want to remove
                    const n = document.querySelector(sheet['selector'])

                    // remove if it exists
                    if (n !== null) {
                        n.remove()
                    }
                }
            }
        }
    }
});