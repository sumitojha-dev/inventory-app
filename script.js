const API = "https://inventory-app-lz4o.onrender.com";

let isLogin = true;

// AUTH
document.getElementById("auth-form").addEventListener("submit", async (e) => {
    e.preventDefault();

    const email = document.getElementById("auth-email").value;
    const password = document.getElementById("auth-password").value;
    const username = document.getElementById("auth-username").value;

    const url = isLogin ? "/login" : "/register";

    const body = isLogin
        ? { email, password }
        : { username, email, password };

    const res = await fetch(API + url, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(body)
    });

    const data = await res.json();

    if (res.ok) {
        localStorage.setItem("user", JSON.stringify({ username: data.username }));
        showApp(data.username);
    } else {
        alert(data.message);
    }
});

// Toggle
document.getElementById("toggle-auth").onclick = () => {
    isLogin = !isLogin;
    document.getElementById("auth-title").innerText = isLogin ? "Login" : "Register";
    document.getElementById("auth-username").style.display = isLogin ? "none" : "block";
};

// Show App
function showApp(username) {
    document.getElementById("auth-container").style.display = "none";
    document.getElementById("app-container").style.display = "block";
    document.getElementById("username").innerText = username;
    loadProducts();
    loadOrders();
}

// Logout
function logout() {
    localStorage.removeItem("user");
    location.reload();
}

// PRODUCTS
async function loadProducts() {
    const res = await fetch(API + "/products");
    const data = await res.json();

    const list = document.getElementById("products");
    const select = document.getElementById("product-select");

    list.innerHTML = "";
    select.innerHTML = "";

    data.forEach(p => {
        list.innerHTML += `<li>${p.name} (${p.quantity}) 
            <button onclick="deleteProduct('${p._id}')">Delete</button>
        </li>`;

        select.innerHTML += `<option value="${p._id}">${p.name}</option>`;
    });
}

// Add Product
document.getElementById("product-form").addEventListener("submit", async (e) => {
    e.preventDefault();

    const product = {
        name: name.value,
        price: price.value,
        quantity: quantity.value,
        category: category.value
    };

    await fetch(API + "/products", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(product)
    });

    loadProducts();
});

// Delete
async function deleteProduct(id) {
    await fetch(API + "/products/" + id, { method: "DELETE" });
    loadProducts();
}

// ORDERS
async function loadOrders() {
    const res = await fetch(API + "/orders");
    const data = await res.json();

    const list = document.getElementById("orders");
    list.innerHTML = "";

    data.forEach(o => {
        list.innerHTML += `<li>${o.product_name} - ${o.quantity} - ₹${o.total_price}</li>`;
    });
}

// Create Order (FIXED 🔥)
document.getElementById("order-form").addEventListener("submit", async (e) => {
    e.preventDefault();

    const product_id = document.getElementById("product-select").value;
    const quantity = document.getElementById("order-qty").value;

    await fetch(API + "/orders", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ product_id, quantity })
    });

    loadOrders();
    loadProducts();
});