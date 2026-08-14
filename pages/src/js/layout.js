document.querySelectorAll('.navi-con').forEach(element => {
    element.addEventListener('click', function(event) {
        document.querySelectorAll('.navi-con').forEach(el => {el.classList.remove('active')})
        element.classList.add('active')
    })
})