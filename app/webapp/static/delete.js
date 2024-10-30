async function deleteLink(url, token) {
    await fetch(url, {
        method: 'DELETE',
        headers: {
            'X-CSRFToken': token
        }
    })

    location.reload()
}