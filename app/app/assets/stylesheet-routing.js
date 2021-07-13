window.dash_clientside = Object.assign({}, window.dash_clientside, {
    clientside: {
        switchStylesheet: function(url) {

            const INDEX_SELECTOR = 'link[rel=stylesheet][href^="/assets/index-page.css"]'
            const TEXT_SELECTOR = 'link[rel=stylesheet][href^="/assets/text-page.css"]'

            const INDEX_CSS = '/assets/index-page.css'
            const TEXT_CSS = '/assets/text-page.css'


            if (url !== '/') {
                const stylesheet = document.querySelector(INDEX_SELECTOR)

                if (stylesheet !== null) {
                    stylesheet.href = TEXT_CSS
                }
            }
            else {
                const stylesheet = document.querySelector(TEXT_SELECTOR)

                if (stylesheet !== null) {
                    stylesheet.href = INDEX_CSS
                }
            }
        }
    }
});