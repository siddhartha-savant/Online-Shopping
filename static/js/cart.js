var updateBtns = document.getElementsByClassName('update-cart')

// There will be multiple updateBtns as every item listed in store.html will have the corresponding "Add to cart" button
// this is like self in python which is used to point to current instance. dataset is used to access the data custom
// attributes of HTML.
// Now the most important part of what needs to be done is when this event handler is called for logged in user or guest
// For logged in user we want to send date to the backend and add item to the database. But if a user does not have an
// account, we want to simply add some data to the browser and store it.
for(var i=0; i<updateBtns.length; i++){
    updateBtns[i].addEventListener('click', function(){
        var productId = this.dataset.product
        var action = this.dataset.action
        console.log('productId:', productId, 'action:', action)

        console.log('USER:', user)
        if(user === 'AnonymousUser'){
            console.log('Not logged in')
        }else{
            updateUserOrder(productId, action)
        }
    })
}

// For fetch function, the first parameter is where we want to send the data. The second parameter is what kind of data
// that we want to send. The data (esp the body is a JSON object, but to send and receive data to a web server, the
// data has to be in string format. Thus the JSON.stringify method is used. Once we send that data we also want to
// return a promise. We first need to turn this value into JSON data. (We are doing that using the 1st .then method)
// The second .then method is used to send the data that the view is sending back to the template
// fetch api sends the data back to the views.py (server side) and returns a promise to the client side.
// location.reload is used to reload the page. (this is done so as to update the number in red present near the cart)
function updateUserOrder(productId, action){
    console.log('User is logged in, sending data..')

    var url = '/update_item/'

    fetch(url, {
        method: 'POST',
        headers:{
        'Content-Type': 'application/json',
        'X-CSRFToken': csrftoken
        },
        body:JSON.stringify({'productId': productId, 'action': action})
    })

    .then((response)=>{
        return response.json()
    })

    .then((data)=>{
        console.log('data:', data)
        location.reload()
    })

}
