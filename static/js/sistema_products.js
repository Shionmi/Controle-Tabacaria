/* Código de gerenciamento de produtos (localStorage) extraído de sistema_estoque_marina.html */
let products = [];
let editingId = null;
const API = '/api/produtos';

// API-only: sempre requisitar ao servidor; não usa localStorage.
async function fetchProductsFromServer() {
    try {
        const res = await fetch(API);
        if (!res.ok) throw new Error('Erro ao buscar produtos no servidor');
        const list = await res.json();
        products = Array.isArray(list) ? list.map(p=>({
            id: p.id_produto || p.id || null,
            codigo_barras: p.codigo_barras || p.barcode || '',
            name: p.nome || p.name || '',
            description: p.descricao || p.description || '',
            price: Number(p.preco || p.price || 0),
            quantity: Number(p.quantidade || p.quantity || 0),
            category: p.categoria || p.category || '',
            unit: p.unidade || p.unit || ''
        })) : [];
    } catch (err) {
        console.error(err);
        showMessage('Não foi possível carregar produtos do servidor.', 'error');
        products = [];
    }
}

async function addProduct() {
    const name = document.getElementById('productName').value.trim();
    const description = document.getElementById('productDescription').value.trim();
    const price = parseFloat(document.getElementById('productPrice').value) || 0;
    const quantity = parseInt(document.getElementById('productQuantity').value) || 0;
    const category = document.getElementById('productCategory').value.trim();
    const unit = document.getElementById('productUnit').value;

    if (!name || isNaN(price) || isNaN(quantity) || !unit) {
        showMessage('Preencha nome, preço, quantidade e unidade!', 'error');
        return;
    }

    try {
        if (editingId !== null) {
            const res = await fetch(`${API}/${editingId}`, {
                method: 'PUT',
                headers: {'Content-Type':'application/json'},
                body: JSON.stringify({nome:name, categoria:category, preco:price, quantidade:quantity})
            });
            const data = await res.json();
            if (!res.ok) throw new Error(data.erro || 'Falha ao atualizar produto');
            showMessage('Produto atualizado com sucesso!', 'success');
        } else {
            const res = await fetch(API, {
                method: 'POST',
                headers: {'Content-Type':'application/json'},
                body: JSON.stringify({nome:name, categoria:category, preco:price, quantidade:quantity})
            });
            const data = await res.json();
            if (!res.ok) throw new Error(data.erro || 'Falha ao adicionar produto');
            showMessage('Produto adicionado com sucesso!', 'success');
        }

        // Recarrega lista do servidor
        await fetchProductsFromServer();
        renderProducts();
        updateStats();
        clearForm();
    } catch (err) {
        console.error(err);
        showMessage('Erro ao salvar produto. Verifique a conexão e tente novamente.', 'error');
    }
}

function renderProducts() { renderFilteredProducts(products); }

function renderFilteredProducts(productsToRender) {
    const container = document.getElementById('productsList');
    if (!productsToRender || productsToRender.length === 0) {
        container.innerHTML = '<div class="empty-state"><p>Nenhum produto encontrado</p></div>';
        return;
    }

    container.innerHTML = productsToRender.map(p => `
        <div class="product-card">
            <h3>${p.name}</h3>
            <div class="product-info">
                <div><strong>Preço:</strong> R$ ${p.price.toFixed(2)}</div>
                <div><strong>Quantidade:</strong> ${p.quantity} ${p.unit}</div>
                ${p.category ? '<div><strong>Categoria:</strong> ' + p.category + '</div>' : ''}
                <div><strong>Código:</strong> ${p.barcode}</div>
            </div>
            <div class="product-actions">
                <button class="btn-success" onclick="openBarcodeModal(${p.id})">📊 Código</button>
                <button class="btn-secondary" onclick="editProduct(${p.id})">✏️ Editar</button>
                <button class="btn-danger" onclick="deleteProduct(${p.id})">🗑️ Remover</button>
            </div>
        </div>
    `).join('');
}

function openBarcodeModal(productId) {
    const product = products.find(p => p.id === productId);
    if (!product) return;

    const nameEl = document.getElementById('barcodeProductName');
    const modal = document.getElementById('barcodeModal');
    if (nameEl) nameEl.textContent = product.name;
    if (modal) modal.classList.add('active');

    setTimeout(() => {
        if (window.JsBarcode) JsBarcode("#barcode", product.barcode || product.codigo_barras || '', { format: "CODE128", width: 2, height: 100, displayValue: true });
    }, 100);
}

function closeModal() { const modal = document.getElementById('barcodeModal'); if (modal) modal.classList.remove('active'); }

function printBarcode() { window.print(); }

async function deleteProduct(productId) {
    if (!confirm('Tem certeza que deseja remover este produto?')) return;
    try {
        const res = await fetch(`${API}/${productId}`, { method: 'DELETE' });
        if (!res.ok) throw new Error('Falha ao remover');
        products = products.filter(p => p.id !== productId);
        localStorage.setItem('products', JSON.stringify(products));
        renderProducts();
        updateStats();
        showMessage('Produto removido com sucesso.', 'success');
    } catch (err) {
        // fallback offline
        products = products.filter(p => p.id !== productId);
        localStorage.setItem('products', JSON.stringify(products));
        renderProducts();
        updateStats();
        showMessage('Produto removido (offline)', 'success');
    }
}

function editProduct(productId) {
    const product = products.find(p => p.id === productId);
    if (!product) return;

    document.getElementById('productName').value = product.name;
    document.getElementById('productDescription').value = product.description;
    document.getElementById('productPrice').value = product.price;
    document.getElementById('productQuantity').value = product.quantity;
    document.getElementById('productCategory').value = product.category;
    document.getElementById('productUnit').value = product.unit;

    editingId = productId;
    const addBtn = document.getElementById('addBtn');
    if (addBtn) addBtn.textContent = 'Salvar';
}

function clearForm() {
    const ids = ['productName','productDescription','productPrice','productQuantity','productCategory','productUnit'];
    ids.forEach(id => { const el = document.getElementById(id); if (el) el.value = ''; });
    editingId = null;
    const addBtn = document.getElementById('addBtn'); if (addBtn) addBtn.textContent = '+ Adicionar';
}

function showMessage(text, type) {
    const container = document.getElementById('successMessage');
    if (!container) return;
    const className = type === 'success' ? 'success-message' : 'error-message';
    container.innerHTML = '<div class="' + className + '">' + text + '</div>';
    setTimeout(() => { container.innerHTML = ''; }, 3000);
}

function updateStats() {
    const totalEl = document.getElementById('totalProducts');
    const valEl = document.getElementById('totalValue');
    if (totalEl) totalEl.textContent = products.length;
    const total = products.reduce((sum, p) => sum + (p.price * p.quantity), 0);
    if (valEl) valEl.textContent = 'R$ ' + total.toFixed(2);
}

function searchProducts() {
    const el = document.getElementById('searchProduct');
    if (!el) return renderProducts();
    const searchTerm = el.value.trim().toLowerCase();
    if (!searchTerm) { renderProducts(); return; }

    const exactMatches = products.filter(product =>
        (product.name || '').toLowerCase() === searchTerm ||
        (product.barcode || '').toLowerCase() === searchTerm ||
        (product.category || '').toLowerCase() === searchTerm ||
        String(product.id) === searchTerm
    );

    if (exactMatches.length > 0) { renderFilteredProducts(exactMatches); return; }

    const filteredProducts = products.filter(product =>
        (product.name || '').toLowerCase().includes(searchTerm) ||
        (product.description || '').toLowerCase().includes(searchTerm) ||
        (product.category || '').toLowerCase().includes(searchTerm) ||
        (product.barcode || '').toLowerCase().includes(searchTerm)
    );

    renderFilteredProducts(filteredProducts);
}

document.addEventListener('DOMContentLoaded', async () => {
    const modal = document.getElementById('barcodeModal');
    if (modal) modal.addEventListener('click', (e) => { if (e.target.id === 'barcodeModal') closeModal(); });
    await fetchProductsFromServer();
    renderProducts();
    updateStats();
    // expose for inline onclick handlers
    window.addProduct = addProduct;
    window.openBarcodeModal = openBarcodeModal;
    window.closeModal = closeModal;
    window.printBarcode = printBarcode;
    window.deleteProduct = deleteProduct;
    window.editProduct = editProduct;
    window.clearForm = clearForm;
    window.searchProducts = searchProducts;
});
