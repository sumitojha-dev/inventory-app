// 🌐 LIVE BACKEND
const API = "https://inventory-app-lz4o.onrender.com";

let isLogin = true;

// ---------------- AUTH ----------------
document.getElementById("auth-form").addEventListener("submit", async (e) => {
    e.preventDefault();

    const email = document.getElementById("auth-email").value;
    const password = document.getElementById("auth-password").value;
    const username = document.getElementById("auth-username").value;

    const url = isLogin ? "/login" : "/register";

    const body = isLogin
        ? { email, password }
        : { username, email, password };

    try {
        alert("If slow, server may be waking up ⏳");

        const res = await fetch(API + url, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify(body)
        });

        const data = await res.json();

        if (res.ok) {
            localStorage.setItem("user", JSON.stringify({
                username: data.username || username
            }));

            showApp(data.username || username);
        } else {
            alert(data.message || "Something went wrong");
        }

    } catch (err) {
        console.error("Auth error:", err);
        alert("Server not reachable ❌");
    }
});

// Toggle Login/Register
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

// Auto login (safe)
try {
    const user = JSON.parse(localStorage.getItem("user"));
    if (user && user.username) {
        showApp(user.username);
    }
} catch {}

// Logout
function logout() {
    localStorage.removeItem("user");
    location.reload();
}

// ---------------- PRODUCTS ----------------
async function loadProducts() {
    try {
        const res = await fetch(API + "/products");
        const data = await res.json();

        if (!Array.isArray(data)) return;

        const list = document.getElementById("products");
        const select = document.getElementById("product-select");

        list.innerHTML = "";
        select.innerHTML = "";

        data.forEach(p => {
            list.innerHTML += `
                <li>
                    ${p.name} (${p.quantity}) 
                    <button onclick="deleteProduct('${p._id}')">Delete</button>
                </li>
            `;

            select.innerHTML += `<option value="${p._id}">${p.name}</option>`;
        });

    } catch (err) {
        console.error("Error loading products:", err);
        alert("Failed to load products");
    }
}

// Add Product
document.getElementById("product-form").addEventListener("submit", async (e) => {
    e.preventDefault();

    const product = {
        name: document.getElementById("name").value,
        price: document.getElementById("price").value,
        quantity: document.getElementById("quantity").value,
        category: document.getElementById("category").value
    };

    // ✅ Validation
    if (!product.name || !product.price || !product.quantity) {
        alert("Fill all fields");
        return;
    }

    try {
        await fetch(API + "/products", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify(product)
        });

        e.target.reset();
        loadProducts();

    } catch (err) {
        console.error("Add product error:", err);
        alert("Failed to add product");
    }
});

// Delete Product
async function deleteProduct(id) {
    try {
        await fetch(API + "/products/" + id, { method: "DELETE" });
        loadProducts();
    } catch (err) {
        console.error("Delete error:", err);
    }
}

// ---------------- ORDERS ----------------
async function loadOrders() {
    try {
        const res = await fetch(API + "/orders");
        const data = await res.json();

        if (!Array.isArray(data)) return;

        const list = document.getElementById("orders");
        list.innerHTML = "";

        data.forEach(o => {
            list.innerHTML += `
                <li>
                    ${o.product_name} - ${o.quantity} - ₹${o.total_price}
                </li>
            `;
        });

    } catch (err) {
        console.error("Error loading orders:", err);
    }
}

// Create Order
document.getElementById("order-form").addEventListener("submit", async (e) => {
    e.preventDefault();

    const product_id = document.getElementById("product-select").value;
    const quantity = document.getElementById("order-qty").value;

    if (!product_id || !quantity) {
        alert("Select product and quantity");
        return;
    }

    try {
        await fetch(API + "/orders", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ product_id, quantity })
        });

        e.target.reset();
        loadOrders();
        loadProducts();

    } catch (err) {
        console.error("Order error:", err);
        alert("Failed to place order");
    }
});