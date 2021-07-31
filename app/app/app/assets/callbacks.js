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

const switchStylesheet = function (url) {

}


window.dash_clientside = Object.assign({}, window.dash_clientside, {
    clientside: {

        /**
         * Switch between stylesheet when rerouting occurs.
         * */
        switchStylesheetCallback: function(url) {

            const INDEX_SELECTOR = 'link[rel=stylesheet][href^="/assets/index-page.css"]'
            const TEXT_SELECTOR = 'link[rel=stylesheet][href^="/assets/text-page.css"]'
            const VALIDATION_SELECTOR = 'link[rel=stylesheet][href^="/assets/validation-page.css"]'

            const INDEX_CSS = '/assets/index-page.css'
            const TEXT_CSS = '/assets/text-page.css'
            const VALIDATION_CSS = '/assets/validation-page.css'

            const INDEX_NODE = document.querySelector(INDEX_SELECTOR)
            const TEXT_NODE = document.querySelector(TEXT_SELECTOR)
            const VALIDATION_NODE = document.querySelector(VALIDATION_SELECTOR)


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
                }
            }

            // in case the url doesn't exist, use the index sheet
            if (!STYLESHEETS.hasOwnProperty(url)) {
                url = '/'
            }

            //
            const node = document.querySelector(STYLESHEETS[url]['selector']);

            if (node === null) {
                addStyleSheet(STYLESHEETS[url]['css'])
            }

            for (let u of Object.keys(STYLESHEETS)) {
                const sheet = STYLESHEETS[u]
                if (u !== url && sheet['css'] !== STYLESHEETS[url]['css']) {
                    const n = document.querySelector(sheet['selector'])
                    if (n !== null) {
                        n.remove()
                    }
                }
            }
        }
    }
});