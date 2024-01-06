function addToTicket(id, ten_chuyen_bay, gia){
    event.preventDefault()

    fetch('/api/add-ticket', {
        method: 'post',
        body: JSON.stringify({
            'id': id,
            'ten_chuyen_bay': ten_chuyen_bay,
            'gia': gia,
        }),
        headers: {
            'Content-Type': 'application/json'
        }
    }).then(function(res) {
        console.info(res)
        return res.json()
    }).then(function(data) {
        console.info(data)

        let counter = document.getElementsByClassName('ticket-counter')
        for (let i = 0; i < counter.length; i++ )
            counter[i].innerText = data.total_quantity
    }).catch(function(err) {
        console.error(err)
    })
}
function pay() {
    var banks = "sacombank";
    var accounts = "123456";
    var bank = document.getElementById("bank").value;
    var account = document.getElementById("account").value;
    if (confirm('Bạn chắc chắn muốn thanh toán không?') == true && bank == banks && account == accounts ){
        fetch('/api/pay', {
            method: 'post',
        }).then(res => res.json()).then(data => {
            if (data.code == 200){
                //location.reload()
                window.location.href="/ticket"
                alert("Thanh toán online thành công")
        }).catch(err => console.error(err))
    }
}

function updateTicket(id, obj) {
    fetch('/api/update-ticket', {
        method: 'put',
        body: JSON.stringify({
            'id': id,
            'quantity': parseInt(obj.value),
        }),
        headers: {
            'Content-Type': 'application/json'
        }
    }).then(res => res.json()).then(data => {
        let counter = document.getElementsByClassName('ticket-counter')
        for (let i = 0; i < counter.length; i++ )
            counter[i].innerText = data.total_quantity

        let amount = document.getElementById('total-amount')
        amount.innerText = new Intl.NumberFormat().format(data.total_amount)
    })
}

function deleteTicket(id) {
    if (confirm('Bạn chắc chắn xoá vé này không?') == true){
        fetch('/api/delete-ticket/' + id , {
            method: 'delete',
            headers: {
                'Content-Type': 'application/json'
            }
        }).then(res => res.json()).then(data => {
        let counter = document.getElementsByClassName('ticket-counter')
        for (let i = 0; i < counter.length; i++ )
            counter[i].innerText = data.total_quantity

        let amount = document.getElementById('total-amount')
        amount.innerText = new Intl.NumberFormat().format(data.total_amount)

        let e = document.getElementById('flight' + id)
        e.style.display = "none"
    }).catch(err => console.error(err))
  }
}

function addComment(flightId) {
    let content = document.getElementById('commentId')
    if (content !== null ){
         fetch('/api/comment', {
            method: 'post',
            body: JSON.stringify({
            'flight_id': flightId,
            'content': content.value,
        }),
            headers: {
                'Content-Type': 'application/json'
            }
        }).then(res => res.json()).then(data => {
            if (data.status == 201){
                let c = data.comment

                let area = document.getElementById('commentArea')

                area.innerHTML = `
                        <br></br>
                        <div class="row">
                            <div class="col-md-2 col-xs-4">
                                <img src="${c.user.avatar}" class="img-fluid rounded-circle" alt="demo" />
                            </div>
                            <div class="col-md-10 col-xs-8">
                                <p> ${c.content} </p>
                                <p><em> ${moment(c.created_date).locale('vi').fromNow()}</em></p>
                            </div>
                        </div>
                ` + area.innerHTML

            } else if (data.status == 404)
                alert(data.err_msg)
        })
    }
}