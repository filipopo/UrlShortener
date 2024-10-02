const el = document.getElementById('sec')

setInterval(() => {
    const num = Number(el.innerHTML)
    if (num > 0)
        el.innerHTML = num - 1
}, 1000)