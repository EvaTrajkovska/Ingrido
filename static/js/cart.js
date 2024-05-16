let updateBtns = document.getElementsByClassName('item');
for ( let i=0; i<updateBtns.length; i++ ){
    updateBtns[i].addEventListener('click',function (){
        let productId = this.dataset.product
        console.log()
        console.log('productId: ' + productId);

        console.log("User: ", user)
        if (user == "AnonymousUser"){
            console.log("User is not authenticated")
        }else{
             goToDetailedView(productId);
        }
    })
}

let updateB = document.getElementsByClassName('menu');
for ( let i=0; i<updateB.length; i++ ){
    updateB[i].addEventListener('click',function (){
        let menuId = this.dataset.product
        console.log()
        console.log('menuId: ' + menuId);

        console.log("User: ", user)
        if (user == "AnonymousUser"){
            console.log("User is not authenticated")
        }else{
             goToDetailedViewMenu(menuId);
        }
    })
}

let addToCart = document.getElementById("addToCart");
if (addToCart !== null){
         addToCart.addEventListener('click', function (){
         console.log('inLisener');
      let productId = this.dataset.product
      let action = this.dataset.action
             console.log(action)
		console.log('productId:'+ productId, 'Action:'+ action)
        console.log('USER:', user)
     if (user === "AnonymousUser"){
             console.log("User is not authenticated")
     }else{
             updateItem(productId,action);
     }
 })
}


let updateInCart = document.getElementsByClassName('update-cart');
for (let i = 0; i < updateInCart.length; i++) {
	updateInCart[i].addEventListener('click', function(){
		let productId = this.dataset.product
		let action = this.dataset.action
		console.log('productId:', productId, 'Action:', action)
		console.log('USER:', user)

		if (user === 'AnonymousUser'){
			console.log('User is not authenticated')

		}else{

			updateItem(productId, action)
		}
	})
}
function updateItem(productId, action){
    let url = '/updateItem/'

    fetch(url, {
        method:'POST',
        headers:{
            'Content-Type':'application/json',
            'X-CSRFToken':csrftoken,
        },
        body:JSON.stringify({'productId':productId, 'action':action})
    })
        .then((response) =>{
            return response.json()
        })
        .then((data) =>{
            console.log('Data: ', data)
            location.assign("http://127.0.0.1:8000/cart/")
        })
}
let deleteButtons = document.getElementsByClassName('delete-cart-item');

for (let i = 0; i < deleteButtons.length; i++) {
    deleteButtons[i].addEventListener('click', function() {
        let productId = this.dataset.product;
        let action = this.dataset.action

        console.log('Deleting product:', productId, 'Action:', action);

        if (user === 'AnonymousUser') {
            console.log('User is not authenticated');
            return;
        }
        deleteCartItem(productId,action);
    });
}

function deleteCartItem(productId,action) {
    let url = '/deleteCartItem/'

    fetch(url, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': csrftoken
        },
        body: JSON.stringify(
{'productId':productId, 'action':action        })
    })
     .then((response) =>{
         console.log("Eva")
            return response.json()
        })
        .then((data) =>{
            console.log('Data: ', data)
            location.assign("http://127.0.0.1:8000/cart/")
        })
}


function goToDetailedView(productId){
    console.log('User is authenticated, sending data..')

    let url = '/go_to_detailed_view/'

    fetch(url, {
        method:'POST',
        headers:{
            'Content-Type':'application/json',
            'X-CSRFToken':csrftoken,
        },
        body:JSON.stringify({'productId':productId})
    })
        .then((response) =>{
            return response.json()
        })
        .then((data) =>{
            console.log('Data: ', data)
            location.assign("http://127.0.0.1:8000/detailedView/")
        })
}
function goToDetailedViewMenu(menuId){
    console.log('Menu data')

    let url = '/go_to_detailed_view_menu/'

    fetch(url, {
        method:'POST',
        headers:{
            'Content-Type':'application/json',
            'X-CSRFToken':csrftoken,
        },
        body:JSON.stringify({'menuId': menuId})
    })
        .then((response) =>{
            return response.json()
        })
        .then((data) =>{
            console.log('Data: ', data)
            location.assign("http://127.0.0.1:8000/menu/")
        })
}

