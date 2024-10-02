let url = new URL(window.location.href)
url = url.pathname.slice(1)

for (let id of ['visit', 'create']) {
    const el = document.getElementById(id)
    el.href += url
    el.innerHTML += url
}