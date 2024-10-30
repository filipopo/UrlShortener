const urlParams = new URLSearchParams(window.location.search)

for (let i of ['url', 'path', 'note']) {
    if (urlParams.get(i))
        document.getElementById(i).value = urlParams.get(i)
}