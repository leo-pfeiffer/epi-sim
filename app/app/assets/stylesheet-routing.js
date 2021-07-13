const addStyleSheet = function(url) {
    const link = document.createElement('link')
    link.href = url
    link.rel = 'stylesheet'

    const head = document.querySelector('head')
    head.appendChild(link)
}


window.dash_clientside = Object.assign({}, window.dash_clientside, {
    clientside: {
        switchStylesheet: function(url) {

            const INDEX_SELECTOR = 'link[rel=stylesheet][href^="/assets/index-page.css"]'
            const TEXT_SELECTOR = 'link[rel=stylesheet][href^="/assets/text-page.css"]'

            const INDEX_CSS = '/assets/index-page.css'
            const TEXT_CSS = '/assets/text-page.css'

            const INDEX_NODE = document.querySelector(INDEX_SELECTOR)
            const TEXT_NODE = document.querySelector(TEXT_SELECTOR)


            // text pages
            if (url !== '/') {
                // add text page CSS if it doesn't exist
                if (TEXT_NODE === null) {
                    addStyleSheet(TEXT_CSS)
                }
                // remove index page CSS if it exists
                if (INDEX_NODE !== null) {
                    INDEX_NODE.remove()
                }
            }

            // index page
            else {
                // add index page CSS if it doesn't exist
                if (INDEX_NODE === null) {
                    addStyleSheet(INDEX_CSS)
                }
                // remove text page CSS if it exists
                if (TEXT_NODE !== null) {
                    TEXT_NODE.remove()
                }
            }
        }
    }
});