/**
 * MunchBite - Modern Interactive Food Ordering & Dynamic Cart Engine
 * Handles real-time food grid filtering, quantity toggling, sliding cart drawer,
 * tax/delivery fee calculations, checkout modal, and AI concierge auto-fill.
 */

(function () {
  'use strict';

  // Accurate Dish Title to High-Resolution Unsplash Image Mapping (Zero Duplicate Images)
  function getFoodItemImage(name, category) {
    const n = (name || '').toLowerCase().trim();
    const c = (category || '').toLowerCase().trim();

    // 1. Seafood & Fish
    if (n.includes('fish') || n.includes('seafood') || c === 'seafood') {
      return 'https://images.unsplash.com/photo-1534422298391-e4f8c172dddb?w=500&auto=format&fit=crop&q=60';
    }

    // 2. Desserts (Brownie vs Gulab Jamun)
    if (n.includes('brownie') || n.includes('lava')) {
      return 'https://images.unsplash.com/photo-1606313564200-e75d5e30476c?w=500&auto=format&fit=crop&q=60';
    }
    if (n.includes('gulab') || n.includes('jamun')) {
      return 'https://images.unsplash.com/photo-1551024709-8f23befc6f87?w=500&auto=format&fit=crop&q=60';
    }

    // 2. Biryani & Rice Items (Student vs Beef/Dum vs Chicken)
    if (n.includes('student') || n.includes('pulao')) {
      return 'https://images.unsplash.com/photo-1633945274405-b6c8069047b0?w=500&auto=format&fit=crop&q=60';
    }
    if ((n.includes('beef') || n.includes('mutton') || n.includes('dum') || n.includes('handi')) && (n.includes('biryani') || n.includes('rice') || c === 'biryani')) {
      return 'https://images.unsplash.com/photo-1589302168068-964664d93dc0?w=500&auto=format&fit=crop&q=60';
    }
    if (n.includes('biryani') || n.includes('rice') || c === 'biryani') {
      return 'https://images.unsplash.com/photo-1563379091339-03b21ab4a4f8?w=500&auto=format&fit=crop&q=60';
    }

    // 3. Pizzas (Chicken/Classic vs Spicy Tikka vs Pepperoni/Fajita)
    if (n.includes('tikka') && (n.includes('pizza') || c === 'pizza')) {
      return 'https://images.unsplash.com/photo-1565299624946-b28f40a0ae38?w=500&auto=format&fit=crop&q=60';
    }
    if (n.includes('pepperoni') || n.includes('fajita')) {
      return 'https://images.unsplash.com/photo-1534308983496-4fabb1a015ee?w=500&auto=format&fit=crop&q=60';
    }
    if (n.includes('pizza') || c === 'pizza') {
      return 'https://images.unsplash.com/photo-1513104890138-7c749659a591?w=500&auto=format&fit=crop&q=60';
    }

    // 4. Burgers (Spicy Zinger vs Beef/Gourmet/Double vs Chicken)
    if (n.includes('zinger')) {
      return 'https://images.unsplash.com/photo-1625813506062-0aeb1d7a094b?w=500&auto=format&fit=crop&q=60';
    }
    if ((n.includes('beef') || n.includes('double') || n.includes('patty') || n.includes('smash') || n.includes('gourmet')) && (n.includes('burger') || c === 'burger' || c === 'burgers')) {
      return 'https://images.unsplash.com/photo-1550547660-d9450f859349?w=500&auto=format&fit=crop&q=60';
    }
    if (n.includes('burger') || c === 'burger' || c === 'burgers') {
      return 'https://images.unsplash.com/photo-1568901346375-23c9450c58cd?w=500&auto=format&fit=crop&q=60';
    }

    // 5. Drinks (Soft Drink/Can vs Lemonade vs Shake)
    if (n.includes('milkshake') || n.includes('shake') || n.includes('coffee')) {
      return 'https://images.unsplash.com/photo-1572490122747-3968b75cc699?w=500&auto=format&fit=crop&q=60';
    }
    if (n.includes('lemonade') || n.includes('margarita') || n.includes('mint') || n.includes('lime')) {
      return 'https://images.unsplash.com/photo-1513558161293-cdaf765ed2fd?w=500&auto=format&fit=crop&q=60';
    }
    if (n.includes('soft') || n.includes('soda') || n.includes('cola') || n.includes('can') || n.includes('sprite') || n.includes('dew') || c === 'drinks') {
      return 'https://images.unsplash.com/photo-1622483767028-3f66f32aef97?w=500&auto=format&fit=crop&q=60';
    }

    // 6. Sides & BBQ (Wings vs Fries vs Reshmi Kabab vs Tikka/Boti)
    if (n.includes('wing') || n.includes('nugget')) {
      return 'https://images.unsplash.com/photo-1562967914-608f82629710?w=500&auto=format&fit=crop&q=60';
    }
    if (n.includes('fries')) {
      return 'https://images.unsplash.com/photo-1573080496219-bb080dd4f877?w=500&auto=format&fit=crop&q=60';
    }
    if (n.includes('reshmi') || n.includes('kabab') || n.includes('seekh') || n.includes('tikka') || n.includes('boti') || n.includes('bbq') || n.includes('malai')) {
      return 'https://images.unsplash.com/photo-1555939594-58d7cb561ad1?w=500&auto=format&fit=crop&q=60';
    }

    if (c === 'desserts') {
      return 'https://images.unsplash.com/photo-1551024709-8f23befc6f87?w=500&auto=format&fit=crop&q=60';
    }
    return 'https://images.unsplash.com/photo-1546069901-ba9599a7e63c?w=500&auto=format&fit=crop&q=60';
  }

  // High-Resolution Food Menu Items with Dedicated, Unique CDN/Unsplash URLs
  const FOOD_ITEMS = [
    // --- Food Palace (Clifton - Restaurant ID: 2) ---
    {
      id: 201,
      restaurantId: 2,
      name: "Special Beef Biryani",
      category: "biryani",
      restaurant: "Food Palace",
      price: 550,
      rating: 4.9,
      reviewsCount: 168,
      prepTime: "25 min",
      isSpicy: true,
      badge: "Clifton Favorite 🔥",
      image: "https://images.unsplash.com/photo-1589302168068-964664d93dc0?w=500&auto=format&fit=crop&q=60",
      description: "Richly spiced Karachi-style beef biryani cooked with tender prime veal cuts, fragrant saffron basmati rice, and mint cucumber raita."
    },
    {
      id: 202,
      restaurantId: 2,
      name: "Cheesy Gourmet Burger",
      category: "burgers",
      restaurant: "Food Palace",
      price: 620,
      rating: 4.8,
      reviewsCount: 122,
      prepTime: "20 min",
      isSpicy: false,
      badge: "Double Cheese",
      image: "https://images.unsplash.com/photo-1550547660-d9450f859349?w=500&auto=format&fit=crop&q=60",
      description: "Thick grilled prime beef patty topped with molten Wisconsin cheddar, caramelized sweet onions, and truffle aioli glaze."
    },
    {
      id: 7,
      restaurantId: 2,
      name: "Chicken Burger",
      category: "burgers",
      restaurant: "Food Palace",
      price: 450,
      rating: 4.7,
      reviewsCount: 88,
      prepTime: "15 min",
      isSpicy: false,
      badge: "Crispy Fillet",
      image: "https://images.unsplash.com/photo-1568901346375-23c9450c58cd?w=500&auto=format&fit=crop&q=60",
      description: "Crispy chicken breast fillet on toasted brioche with fresh lettuce and tangy herb mayo."
    },
    {
      id: 9,
      restaurantId: 2,
      name: "Spicy Zinger Burger",
      category: "burgers",
      restaurant: "Food Palace",
      price: 480,
      rating: 4.8,
      reviewsCount: 96,
      prepTime: "15 min",
      isSpicy: true,
      badge: "Fiery Crunch 🔥",
      image: "https://images.unsplash.com/photo-1625813506062-0aeb1d7a094b?w=500&auto=format&fit=crop&q=60",
      description: "Hand-breaded crunchy chicken breast fillet tossed in fiery seasonings with fresh iceberg lettuce and garlic mayo."
    },
    {
      id: 5,
      restaurantId: 2,
      name: "Chicken Pizza",
      category: "pizza",
      restaurant: "Food Palace",
      price: 950,
      rating: 4.8,
      reviewsCount: 130,
      prepTime: "25 min",
      badge: "Classic Cheese",
      image: "https://images.unsplash.com/photo-1513104890138-7c749659a591?w=500&auto=format&fit=crop&q=60",
      description: "Medium hand-stretched pizza loaded with seasoned grilled chicken, mozzarella, and herb marinara."
    },
    {
      id: 6,
      restaurantId: 2,
      name: "Spicy Chicken Tikka Pizza",
      category: "pizza",
      restaurant: "Food Palace",
      price: 1100,
      rating: 4.9,
      reviewsCount: 215,
      prepTime: "25 min",
      isSpicy: true,
      badge: "Chef's Special 🍕",
      image: "https://images.unsplash.com/photo-1565299624946-b28f40a0ae38?w=500&auto=format&fit=crop&q=60",
      description: "Crispy hand-tossed artisan crust topped with charcoal-smoked chicken tikka, rich mozzarella, sweet onions, and jalapeños."
    },
    {
      id: 203,
      restaurantId: 2,
      name: "Loaded Fries",
      category: "sides",
      restaurant: "Food Palace",
      price: 320,
      rating: 4.8,
      reviewsCount: 94,
      prepTime: "15 min",
      isSpicy: true,
      badge: "Loaded & Crispy",
      image: "https://images.unsplash.com/photo-1573080496219-bb080dd4f877?w=500&auto=format&fit=crop&q=60",
      description: "Golden skin-on potato fries smothered in warm liquid cheddar, smoky chicken bits, sliced jalapeños and signature ranch drizzle."
    },
    {
      id: 204,
      restaurantId: 2,
      name: "Mint Lemonade",
      category: "drinks",
      restaurant: "Food Palace",
      price: 180,
      rating: 4.9,
      reviewsCount: 80,
      prepTime: "5 min",
      isSpicy: false,
      badge: "Refreshing 🍃",
      image: "https://images.unsplash.com/photo-1513558161293-cdaf765ed2fd?w=500&auto=format&fit=crop&q=60",
      description: "Hand-blended fresh garden mint leaves, freshly squeezed lime juice, Himalayan rock salt, and crushed ice for instant revival."
    },
    {
      id: 10,
      restaurantId: 2,
      name: "Soft Drink",
      category: "drinks",
      restaurant: "Food Palace",
      price: 110,
      rating: 4.6,
      reviewsCount: 50,
      prepTime: "5 min",
      isSpicy: false,
      badge: "Ice Chilled 🧊",
      image: "https://images.unsplash.com/photo-1622483767028-3f66f32aef97?w=500&auto=format&fit=crop&q=60",
      description: "Chilled 345ml soft drink can of your choice, served frosty cold."
    },
    {
      id: 15,
      restaurantId: 2,
      name: "Chocolate Brownie",
      category: "desserts",
      restaurant: "Food Palace",
      price: 300,
      rating: 4.9,
      reviewsCount: 64,
      prepTime: "10 min",
      isSpicy: false,
      badge: "Rich Chocolate 🍫",
      image: "https://images.unsplash.com/photo-1606313564200-e75d5e30476c?w=500&auto=format&fit=crop&q=60",
      description: "Warm Belgian chocolate fudge brownie drizzled with rich melted chocolate sauce."
    },

    // --- Karachi Bites (Gulshan-e-Iqbal - Restaurant ID: 3) ---
    {
      id: 301,
      restaurantId: 3,
      name: "Student Chicken Biryani",
      category: "biryani",
      restaurant: "Karachi Bites",
      price: 420,
      rating: 4.8,
      reviewsCount: 154,
      prepTime: "20 min",
      isSpicy: true,
      badge: "Value Deal ⭐",
      image: "https://images.unsplash.com/photo-1633945274405-b6c8069047b0?w=500&auto=format&fit=crop&q=60",
      description: "Authentic Karachi student-style spicy chicken biryani served steaming hot with golden roasted potatoes & spicy cucumber raita."
    },
    {
      id: 302,
      restaurantId: 3,
      name: "Crispy Zinger Burger",
      category: "burgers",
      restaurant: "Karachi Bites",
      price: 480,
      rating: 4.7,
      reviewsCount: 110,
      prepTime: "15 min",
      isSpicy: true,
      badge: "Hot & Crunchy",
      image: "https://images.unsplash.com/photo-1625813506062-0aeb1d7a094b?w=500&auto=format&fit=crop&q=60",
      description: "Extra large crispy batter-fried chicken thigh fillet with fiery chili seasoning, shredded iceberg lettuce & creamy garlic mayo."
    },
    {
      id: 11,
      restaurantId: 3,
      name: "Chicken Burger",
      category: "burgers",
      restaurant: "Karachi Bites",
      price: 400,
      rating: 4.6,
      reviewsCount: 72,
      prepTime: "15 min",
      isSpicy: false,
      badge: "Classic",
      image: "https://images.unsplash.com/photo-1568901346375-23c9450c58cd?w=500&auto=format&fit=crop&q=60",
      description: "Classic tender chicken burger with seasoned mayo and crispy lettuce in sesame bun."
    },
    {
      id: 13,
      restaurantId: 3,
      name: "French Fries",
      category: "sides",
      restaurant: "Karachi Bites",
      price: 200,
      rating: 4.7,
      reviewsCount: 78,
      prepTime: "10 min",
      isSpicy: false,
      badge: "Crispy Salted",
      image: "https://images.unsplash.com/photo-1573080496219-bb080dd4f877?w=500&auto=format&fit=crop&q=60",
      description: "Golden crispy skin-on salted potato fries served with zesty dipping sauces."
    },
    {
      id: 14,
      restaurantId: 3,
      name: "Spicy Chicken Wings",
      category: "sides",
      restaurant: "Karachi Bites",
      price: 550,
      rating: 4.8,
      reviewsCount: 88,
      prepTime: "15 min",
      isSpicy: true,
      badge: "Spicy Wings 🔥",
      image: "https://images.unsplash.com/photo-1562967914-608f82629710?w=500&auto=format&fit=crop&q=60",
      description: "Six hot, crispy chicken wings tossed in fiery chili garlic sauce."
    },
    {
      id: 303,
      restaurantId: 3,
      name: "Chicken Malai Boti",
      category: "sides",
      restaurant: "Karachi Bites",
      price: 580,
      rating: 4.9,
      reviewsCount: 98,
      prepTime: "20 min",
      isSpicy: false,
      badge: "BBQ Special",
      image: "https://images.unsplash.com/photo-1555939594-58d7cb561ad1?w=500&auto=format&fit=crop&q=60",
      description: "Boneless succulent chicken cubes marinated in fresh clotted cream, white pepper, and mild spices, charcoal-grilled over open coals."
    },
    {
      id: 304,
      restaurantId: 3,
      name: "Soft Drink 500ml",
      category: "drinks",
      restaurant: "Karachi Bites",
      price: 120,
      rating: 4.6,
      reviewsCount: 62,
      prepTime: "5 min",
      isSpicy: false,
      badge: "Ice Chilled 🧊",
      image: "https://images.unsplash.com/photo-1622483767028-3f66f32aef97?w=500&auto=format&fit=crop&q=60",
      description: "Chilled 500ml bottle of your choice (Cola, Sprite, Dew) served ice-cold with fresh lemon slice."
    },

    // --- Spice Garden (Tariq Road - Restaurant ID: 1) ---
    {
      id: 101,
      restaurantId: 1,
      name: "Handi Dum Biryani",
      category: "biryani",
      restaurant: "Spice Garden",
      price: 680,
      rating: 4.9,
      reviewsCount: 176,
      prepTime: "25 min",
      isSpicy: true,
      badge: "Signature Handi 🔥",
      image: "https://images.unsplash.com/photo-1589302168068-964664d93dc0?w=500&auto=format&fit=crop&q=60",
      description: "Slow-cooked saffron dum basmati rice layered with tender marinated meat, baby potatoes, aromatic whole spices & cooling mint raita."
    },
    {
      id: 1,
      restaurantId: 1,
      name: "Chicken Biryani",
      category: "biryani",
      restaurant: "Spice Garden",
      price: 450,
      rating: 4.9,
      reviewsCount: 142,
      prepTime: "20 min",
      isSpicy: true,
      badge: "Bestseller 🔥",
      image: "https://images.unsplash.com/photo-1563379091339-03b21ab4a4f8?w=500&auto=format&fit=crop&q=60",
      description: "Fragrant basmati rice layered with tender marinated chicken, golden potatoes, saffron, and spicy raita."
    },
    {
      id: 2,
      restaurantId: 1,
      name: "Beef Biryani",
      category: "biryani",
      restaurant: "Spice Garden",
      price: 520,
      rating: 4.8,
      reviewsCount: 94,
      prepTime: "25 min",
      isSpicy: true,
      badge: "Tender Veal",
      image: "https://images.unsplash.com/photo-1589302168068-964664d93dc0?w=500&auto=format&fit=crop&q=60",
      description: "Slow-cooked Karachi beef biryani with tender boneless meat and rich aromatic spices."
    },
    {
      id: 102,
      restaurantId: 1,
      name: "Classic Italian Pizza",
      category: "pizza",
      restaurant: "Spice Garden",
      price: 1150,
      rating: 4.8,
      reviewsCount: 140,
      prepTime: "30 min",
      isSpicy: false,
      badge: "Wood-Fired Crust",
      image: "https://images.unsplash.com/photo-1513104890138-7c749659a591?w=500&auto=format&fit=crop&q=60",
      description: "Thin Italian artisan crust baked over oak embers with rich crushed tomato sauce, fresh buffalo mozzarella, and aromatic sweet basil."
    },
    {
      id: 103,
      restaurantId: 1,
      name: "Chicken Seekh Kabab",
      category: "BBQ & Sides",
      restaurant: "Spice Garden",
      price: 590,
      rating: 4.9,
      reviewsCount: 115,
      prepTime: "20 min",
      isSpicy: true,
      badge: "Melt in Mouth",
      image: "https://images.unsplash.com/photo-1555939594-58d7cb561ad1?w=500&auto=format&fit=crop&q=60",
      description: "Tender minced chicken skewers char-grilled over open coals with fresh spices and mint chutney."
    },
    {
      id: 104,
      restaurantId: 1,
      name: "Crispy Finger Fish",
      category: "seafood",
      restaurant: "Spice Garden",
      price: 650,
      rating: 4.8,
      reviewsCount: 88,
      prepTime: "20 min",
      isSpicy: false,
      badge: "Golden Crispy 🐟",
      image: "https://images.unsplash.com/photo-1534422298391-e4f8c172dddb?w=500&auto=format&fit=crop&q=60",
      description: "Golden crispy fried fish fillets served with spicy tartar sauce and lemon wedges."
    },
    {
      id: 3,
      restaurantId: 1,
      name: "Soft Drink",
      category: "drinks",
      restaurant: "Spice Garden",
      price: 120,
      rating: 4.7,
      reviewsCount: 52,
      prepTime: "5 min",
      isSpicy: false,
      badge: "Ice Cold 🧊",
      image: "https://images.unsplash.com/photo-1622483767028-3f66f32aef97?w=500&auto=format&fit=crop&q=60",
      description: "Chilled 345ml refreshing soda can served ice-cold to elevate and balance your spicy meal."
    }
  ];

  const STANDARD_DELIVERY_FEE = 150;
  const TAX_RATE = 0.05; // 5% Standard Tax

  // Cart State (stored in localStorage)
  let cart = {};

  function loadCart() {
    try {
      const stored = localStorage.getItem('munchbite_cart_items');
      if (stored) {
        cart = JSON.parse(stored);
      } else {
        cart = {};
      }
    } catch (e) {
      cart = {};
    }
  }

  function saveCart() {
    try {
      localStorage.setItem('munchbite_cart_items', JSON.stringify(cart));
    } catch (e) {}
    updateAllCartUI();
  }

  function formatRs(num) {
    return 'Rs. ' + Math.round(num || 0).toLocaleString();
  }

  // Calculate live numbers
  function calculateTotals() {
    let subtotal = 0;
    let totalItems = 0;

    Object.entries(cart).forEach(([foodId, qty]) => {
      if (qty > 0) {
        const item = FOOD_ITEMS.find(f => f.id === parseInt(foodId));
        if (item) {
          subtotal += item.price * qty;
          totalItems += qty;
        }
      }
    });

    const deliveryFee = totalItems > 0 ? STANDARD_DELIVERY_FEE : 0;
    const tax = totalItems > 0 ? Math.round(subtotal * TAX_RATE) : 0;
    const grandTotal = totalItems > 0 ? subtotal + deliveryFee + tax : 0;

    return {
      subtotal,
      deliveryFee,
      tax,
      grandTotal,
      totalItems
    };
  }

  // Render the Dynamic Food Grid
  window.renderFoodGrid = function (filterCategory = 'all') {
    const gridContainer = document.getElementById('dynamic-food-grid');
    if (!gridContainer) return;

    const itemsToRender = filterCategory === 'all'
      ? FOOD_ITEMS
      : FOOD_ITEMS.filter(item => {
          const cat = (item.category || '').toLowerCase();
          if (filterCategory === 'sides') {
            return cat.includes('sides') || cat.includes('bbq') || cat === 'seafood';
          }
          if (filterCategory === 'seafood') {
            return cat === 'seafood' || cat.includes('sides');
          }
          return cat === filterCategory.toLowerCase();
        });

    if (itemsToRender.length === 0) {
      gridContainer.innerHTML = `
        <div style="grid-column: 1 / -1; text-align: center; padding: 3rem 1rem; background: #FFFFFF; border-radius: 16px; border: 1px dashed var(--border)">
          <div style="font-size: 2.5rem; margin-bottom: 0.5rem">🍽️</div>
          <h3 style="margin: 0 0 0.4rem; color: var(--text-main)">No items found</h3>
          <p class="meta">No dishes available in this category right now.</p>
        </div>
      `;
      return;
    }

    gridContainer.innerHTML = itemsToRender.map(item => {
      const currentQty = cart[item.id] || 0;
      const isAdded = currentQty > 0;

      return `
        <article class="modern-food-card group" data-category="${item.category}" data-id="${item.id}">
          <!-- Food Image Thumbnail with Hover Zoom -->
          <div class="card-image-wrap">
            <img 
              src="${item.image || getFoodItemImage(item.name, item.category)}" 
              alt="${item.name}" 
              class="card-food-img" 
              loading="lazy"
              onerror="this.onerror=null; this.src='https://images.unsplash.com/photo-1546069901-ba9599a7e63c?w=500&auto=format&fit=crop&q=60';"
            >
            <div class="image-overlay-gradient"></div>

            <!-- Overlaid Badges: Rating & Prep Time -->
            <div class="card-badge-top-left">
              <span class="rating-badge" title="${item.rating} out of 5 stars (${item.reviewsCount} reviews)">
                <svg width="12" height="12" viewBox="0 0 24 24" fill="#F59E0B" stroke="#F59E0B" stroke-width="1">
                  <polygon points="12 2 15.09 8.26 22 9.27 17 14.14 18.18 21.02 12 17.77 5.82 21.02 7 14.14 2 9.27 8.91 8.26 12 2"></polygon>
                </svg>
                <span>${item.rating}</span>
                <span class="rating-reviews-mini">(${item.reviewsCount})</span>
              </span>
            </div>

            <div class="card-badge-top-right">
              <span class="prep-time-badge" title="Estimated preparation and cooking time">
                <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round">
                  <circle cx="12" cy="12" r="10"></circle>
                  <polyline points="12 6 12 12 16 14"></polyline>
                </svg>
                <span>${item.prepTime}</span>
              </span>
            </div>

            <!-- Optional Feature Tag (Spicy / Bestseller) -->
            ${item.badge ? `
              <div class="card-badge-bottom-left">
                <span class="feature-tag-chip ${item.isSpicy ? 'spicy' : ''}">${item.badge}</span>
              </div>
            ` : ''}
          </div>

          <!-- Card Content Body -->
          <div class="card-content-body">
            <div class="card-meta-line">
              <span class="card-restaurant-name">${item.restaurant}</span>
              <span class="meta-dot">&bull;</span>
              <span class="card-category-label">${capitalize(item.category)}</span>
            </div>

            <h3 class="card-dish-name" title="${item.name}">${item.name}</h3>
            
            <p class="card-dish-desc">${item.description}</p>

            <div class="card-footer-row">
              <div class="card-price-wrap">
                <span class="price-val">${formatRs(item.price)}</span>
              </div>

              <!-- Interactive Add to Cart / Quantity Toggle Button -->
              <div class="cart-action-container" data-food-id="${item.id}">
                <button 
                  type="button" 
                  class="btn-add-cart ${isAdded ? 'hidden' : ''}" 
                  onclick="window.addToCart(${item.id})"
                  aria-label="Add ${item.name} to cart"
                >
                  <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round">
                    <line x1="12" y1="5" x2="12" y2="19"></line>
                    <line x1="5" y1="12" x2="19" y2="12"></line>
                  </svg>
                  <span>Add</span>
                </button>

                <div class="qty-control-group ${isAdded ? '' : 'hidden'}">
                  <button 
                    type="button" 
                    class="qty-btn qty-minus" 
                    onclick="window.changeQty(${item.id}, -1)" 
                    aria-label="Decrease quantity"
                  >
                    <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="3" stroke-linecap="round">
                      <line x1="5" y1="12" x2="19" y2="12"></line>
                    </svg>
                  </button>
                  <span class="qty-display">${currentQty}</span>
                  <button 
                    type="button" 
                    class="qty-btn qty-plus" 
                    onclick="window.changeQty(${item.id}, 1)" 
                    aria-label="Increase quantity"
                  >
                    <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="3" stroke-linecap="round">
                      <line x1="12" y1="5" x2="12" y2="19"></line>
                      <line x1="5" y1="12" x2="19" y2="12"></line>
                    </svg>
                  </button>
                </div>
              </div>
            </div>
          </div>
        </article>
      `;
    }).join('');
  };

  function capitalize(str) {
    if (!str) return '';
    return str.charAt(0).toUpperCase() + str.slice(1);
  }

  // Category Filtering
  window.filterCategory = function (categoryName) {
    // Update active button state
    const buttons = document.querySelectorAll('.category-pill-card');
    buttons.forEach(btn => {
      const btnCat = btn.getAttribute('data-category') || 'all';
      if (btnCat.toLowerCase() === categoryName.toLowerCase()) {
        btn.classList.add('active');
      } else {
        btn.classList.remove('active');
      }
    });

    // Re-render food grid with smooth animation
    const grid = document.getElementById('dynamic-food-grid');
    if (grid) {
      grid.style.opacity = '0.4';
      grid.style.transform = 'scale(0.99)';
      setTimeout(() => {
        window.renderFoodGrid(categoryName);
        grid.style.opacity = '1';
        grid.style.transform = 'scale(1)';
      }, 120);
    }
  };

  // Add Item to Cart
  window.addToCart = function (foodId) {
    foodId = parseInt(foodId);
    cart[foodId] = (cart[foodId] || 0) + 1;
    saveCart();
    animateCardButton(foodId);
    showToastNotification("Added to cart! 🛍️");
  };

  // Change Quantity (+1 or -1)
  window.changeQty = function (foodId, delta) {
    foodId = parseInt(foodId);
    const newQty = (cart[foodId] || 0) + delta;
    if (newQty <= 0) {
      delete cart[foodId];
    } else if (newQty > 20) {
      showToastNotification("Maximum limit is 20 units per dish.", true);
      return;
    } else {
      cart[foodId] = newQty;
    }
    saveCart();
  };

  // Remove Item from Cart Completely
  window.removeCartItem = function (foodId) {
    foodId = parseInt(foodId);
    delete cart[foodId];
    saveCart();
    showToastNotification("Item removed from cart");
  };

  // Clear Cart with prompt
  window.clearCartConfirm = function () {
    if (Object.keys(cart).length === 0) return;
    if (confirm("Are you sure you want to clear your cart?")) {
      cart = {};
      saveCart();
      showToastNotification("Cart cleared");
    }
  };

  // Visual button animation on add
  function animateCardButton(foodId) {
    const container = document.querySelector(`.cart-action-container[data-food-id="${foodId}"]`);
    if (container) {
      container.classList.add('pulse-pop');
      setTimeout(() => container.classList.remove('pulse-pop'), 400);
    }
  }

  // Update All UI Components based on current Cart State
  function updateAllCartUI() {
    const totals = calculateTotals();

    // 1. Update Card Controls on the page
    document.querySelectorAll('.cart-action-container').forEach(container => {
      const foodId = parseInt(container.getAttribute('data-food-id'));
      const qty = cart[foodId] || 0;
      const addBtn = container.querySelector('.btn-add-cart');
      const qtyGroup = container.querySelector('.qty-control-group');
      const qtyDisplay = container.querySelector('.qty-display');

      if (addBtn && qtyGroup) {
        if (qty > 0) {
          addBtn.classList.add('hidden');
          qtyGroup.classList.remove('hidden');
          if (qtyDisplay) qtyDisplay.textContent = qty;
        } else {
          addBtn.classList.remove('hidden');
          qtyGroup.classList.add('hidden');
        }
      }
    });

    // 2. Update Navbar Cart Pill
    const navCartPill = document.querySelector('.cart-pill');
    if (navCartPill) {
      const badge = navCartPill.querySelector('.badge');
      if (badge) {
        badge.textContent = totals.totalItems;
      }
    }

    // 3. Update Floating Cart FAB
    const fabBadge = document.getElementById('fab-cart-badge');
    const fabTotal = document.getElementById('fab-cart-total');
    const fabBtn = document.getElementById('floating-cart-fab');
    if (fabBadge) fabBadge.textContent = totals.totalItems;
    if (fabTotal) fabTotal.textContent = formatRs(totals.grandTotal);
    if (fabBtn) {
      if (totals.totalItems > 0) {
        fabBtn.classList.add('visible');
      } else {
        fabBtn.classList.remove('visible');
      }
    }

    // 4. Update Sliding Drawer
    renderCartDrawer(totals);
  }

  // Render Drawer Content
  function renderCartDrawer(totals) {
    const drawerItemsContainer = document.getElementById('cart-drawer-items');
    const countBadge = document.getElementById('drawer-items-count-badge');
    const subtotalEl = document.getElementById('drawer-subtotal');
    const deliveryFeeEl = document.getElementById('drawer-delivery-fee');
    const taxEl = document.getElementById('drawer-tax');
    const grandTotalEl = document.getElementById('drawer-grand-total');
    const checkoutBtnPill = document.getElementById('checkout-btn-total-pill');
    const checkoutBtn = document.getElementById('drawer-checkout-btn');

    if (!drawerItemsContainer) return;

    if (countBadge) {
      countBadge.textContent = totals.totalItems === 1 ? '1 item' : `${totals.totalItems} items`;
    }

    if (totals.totalItems === 0) {
      drawerItemsContainer.innerHTML = `
        <div class="cart-empty-state">
          <div class="empty-icon-bubble">🍲</div>
          <h4 style="margin:0.5rem 0 0.25rem; font-size:1.15rem; color:var(--text-main); font-weight:800">Your cart is hungry!</h4>
          <p style="margin:0 0 1.35rem; color:var(--text-muted); font-size:0.88rem; max-width:26ch">Add delicious dishes from our Karachi kitchens to start ordering.</p>
          <button type="button" class="btn sm" onclick="window.closeCartDrawer(); window.scrollToMenu();">Browse Popular Dishes</button>
        </div>
      `;
      if (checkoutBtn) checkoutBtn.disabled = true;
    } else {
      if (checkoutBtn) checkoutBtn.disabled = false;
      const activeItems = Object.entries(cart)
        .filter(([_, qty]) => qty > 0)
        .map(([id, qty]) => {
          const item = FOOD_ITEMS.find(f => f.id === parseInt(id));
          return { item, qty };
        })
        .filter(entry => entry.item);

      drawerItemsContainer.innerHTML = activeItems.map(({ item, qty }) => `
        <div class="drawer-cart-item-row" data-id="${item.id}">
          <img src="${item.image || getFoodItemImage(item.name, item.category)}" alt="${item.name}" class="drawer-item-thumb" onerror="this.onerror=null; this.src='https://images.unsplash.com/photo-1546069901-ba9599a7e63c?w=500&auto=format&fit=crop&q=60';">
          <div class="drawer-item-info">
            <h4 class="drawer-item-title">${item.name}</h4>
            <div class="drawer-item-price-meta">
              <span class="unit-price">${formatRs(item.price)} each</span>
              <span class="meta-dot">&bull;</span>
              <strong class="line-total">${formatRs(item.price * qty)}</strong>
            </div>
            
            <div class="drawer-item-actions">
              <div class="qty-control-group sm">
                <button type="button" class="qty-btn qty-minus" onclick="window.changeQty(${item.id}, -1)" aria-label="Decrease quantity">−</button>
                <span class="qty-display">${qty}</span>
                <button type="button" class="qty-btn qty-plus" onclick="window.changeQty(${item.id}, 1)" aria-label="Increase quantity">+</button>
              </div>

              <button type="button" class="remove-item-btn" onclick="window.removeCartItem(${item.id})" title="Remove item" aria-label="Remove item">
                <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                  <polyline points="3 6 5 6 21 6"></polyline>
                  <path d="M19 6v14a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2V6m3 0V4a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2"></path>
                </svg>
              </button>
            </div>
          </div>
        </div>
      `).join('');
    }

    if (subtotalEl) subtotalEl.textContent = formatRs(totals.subtotal);
    if (deliveryFeeEl) deliveryFeeEl.textContent = totals.totalItems > 0 ? formatRs(STANDARD_DELIVERY_FEE) : 'Rs. 0';
    if (taxEl) taxEl.textContent = formatRs(totals.tax);
    if (grandTotalEl) grandTotalEl.textContent = formatRs(totals.grandTotal);
    if (checkoutBtnPill) checkoutBtnPill.textContent = formatRs(totals.grandTotal);
  }

  // Drawer Open / Close Functions
  window.openCartDrawer = function () {
    const drawer = document.getElementById('cart-drawer');
    const overlay = document.getElementById('cart-drawer-overlay');
    if (drawer && overlay) {
      drawer.classList.add('open');
      overlay.classList.add('open');
      drawer.setAttribute('aria-hidden', 'false');
      overlay.setAttribute('aria-hidden', 'false');
      document.body.style.overflow = 'hidden'; // prevent background scrolling
    }
  };

  window.closeCartDrawer = function () {
    const drawer = document.getElementById('cart-drawer');
    const overlay = document.getElementById('cart-drawer-overlay');
    if (drawer && overlay) {
      drawer.classList.remove('open');
      overlay.classList.remove('open');
      drawer.setAttribute('aria-hidden', 'true');
      overlay.setAttribute('aria-hidden', 'true');
      document.body.style.overflow = '';
    }
  };

  window.scrollToMenu = function () {
    const section = document.getElementById('popular-food-section') || document.querySelector('.category-strip');
    if (section) {
      section.scrollIntoView({ behavior: 'smooth' });
    }
  };

  // Checkout Modal Open / Close
  window.openCheckoutModal = function () {
    const totals = calculateTotals();
    if (totals.totalItems === 0) {
      showToastNotification("Please add dishes to your cart first!", true);
      return;
    }
    window.closeCartDrawer();

    const modal = document.getElementById('checkout-modal');
    const overlay = document.getElementById('checkout-modal-overlay');
    const grandTotalEl = document.getElementById('modal-grand-total');
    const countEl = document.getElementById('modal-items-count');

    if (grandTotalEl) grandTotalEl.textContent = formatRs(totals.grandTotal);
    if (countEl) countEl.textContent = `${totals.totalItems} ${totals.totalItems === 1 ? 'Dish' : 'Dishes'}`;

    if (modal && overlay) {
      modal.classList.add('open');
      overlay.classList.add('open');
      modal.setAttribute('aria-hidden', 'false');
      overlay.setAttribute('aria-hidden', 'false');
      document.body.style.overflow = 'hidden';
    }
  };

  window.closeCheckoutModal = function () {
    const modal = document.getElementById('checkout-modal');
    const overlay = document.getElementById('checkout-modal-overlay');
    if (modal && overlay) {
      modal.classList.remove('open');
      overlay.classList.remove('open');
      modal.setAttribute('aria-hidden', 'true');
      overlay.setAttribute('aria-hidden', 'true');
      document.body.style.overflow = '';
    }
  };

  // Quick Address Chip autofill
  window.fillAddress = function (addr) {
    const textarea = document.getElementById('checkout-address');
    if (textarea) {
      textarea.value = addr;
      textarea.focus();
    }
  };

  // Handle Order Placement
  window.handlePlaceOrder = function (e) {
    e.preventDefault();
    const btn = document.getElementById('confirm-order-btn');
    const btnText = document.getElementById('btn-order-text');
    const spinner = document.getElementById('order-spinner');

    if (btn) btn.disabled = true;
    if (btnText) btnText.textContent = "Verifying Kitchen Dispatch...";
    if (spinner) spinner.classList.remove('hidden');

    const form = document.getElementById('checkout-form');
    const successView = document.getElementById('checkout-success-state');
    const paymentMethod = form ? (form.querySelector('input[name="payment_method"]:checked')?.value || 'Cash') : 'Cash';
    const randomOrderId = '#MB-' + Math.floor(1000 + Math.random() * 9000);

    setTimeout(() => {
      if (form) form.classList.add('hidden');
      if (successView) {
        successView.classList.remove('hidden');
        const idEl = document.getElementById('success-order-id');
        const payEl = document.getElementById('success-payment-method');
        if (idEl) idEl.textContent = randomOrderId;
        if (payEl) {
          payEl.textContent = paymentMethod === 'Card'
            ? 'Debit / Credit Card (Paid)'
            : (paymentMethod === 'Online' ? 'Online Banking (Verified)' : 'Cash on Delivery');
        }
      }

      // Reset cart
      cart = {};
      saveCart();
      showToastNotification("Order " + randomOrderId + " confirmed! 🚀");
    }, 1200);
  };

  window.finishOrderAndReload = function () {
    window.closeCheckoutModal();
    window.location.reload();
  };

  // AI Concierge Suggestions Auto-fill
  function setupAIConcierge() {
    const input = document.getElementById('concierge-input');
    const chips = document.querySelectorAll('.concierge-prompt-chip');
    const submitBtn = document.getElementById('concierge-submit-btn');

    if (chips && chips.length > 0) {
      chips.forEach(chip => {
        chip.addEventListener('click', function () {
          const promptText = this.getAttribute('data-prompt') || this.innerText.replace(/^["“”]|["“”]$/g, '').trim();
          if (input) {
            input.value = promptText;
            input.focus();
            input.classList.add('input-pulse-glow');
            setTimeout(() => input.classList.remove('input-pulse-glow'), 600);
          }
        });
      });
    }

    if (submitBtn && input) {
      submitBtn.addEventListener('click', function () {
        triggerAIQuery(input.value);
      });
      input.addEventListener('keydown', function (e) {
        if (e.key === 'Enter') {
          e.preventDefault();
          triggerAIQuery(input.value);
        }
      });
    }
  }

  function triggerAIQuery(query) {
    if (!query || !query.trim()) return;
    const cleanQ = query.trim();

    // Check if floating chat widget exists on page
    const chatFab = document.getElementById('chat-fab');
    const chatPanel = document.getElementById('chat-panel');
    const chatInput = document.querySelector('#chat-panel .chat-form input');
    const chatForm = document.querySelector('#chat-panel .chat-form');

    if (chatPanel && chatInput && chatForm) {
      if (chatFab && !chatPanel.classList.contains('open')) {
        chatFab.click();
      }
      chatInput.value = cleanQ;
      chatForm.dispatchEvent(new Event('submit', { cancelable: true }));
      chatPanel.scrollIntoView({ behavior: 'smooth' });
    } else {
      // Redirect to AI Assistant page with query parameter
      window.location.href = '/chatbot?q=' + encodeURIComponent(cleanQ);
    }
  }

  // Toast Notification helper
  function showToastNotification(message, isWarning = false) {
    let toast = document.getElementById('mb-floating-toast');
    if (!toast) {
      toast = document.createElement('div');
      toast.id = 'mb-floating-toast';
      toast.className = 'mb-floating-toast';
      document.body.appendChild(toast);
    }

    toast.textContent = message;
    toast.className = 'mb-floating-toast show ' + (isWarning ? 'warning' : 'success');

    clearTimeout(toast._timeout);
    toast._timeout = setTimeout(() => {
      toast.classList.remove('show');
    }, 2800);
  }

  // Hook into navbar cart button
  function hookNavbarCart() {
    const navCartPill = document.querySelector('.cart-pill');
    if (navCartPill) {
      navCartPill.addEventListener('click', function (e) {
        // Prevent default only if on homepage or we want smooth slide drawer everywhere
        e.preventDefault();
        window.openCartDrawer();
      });
    }
  }

  // Restaurant Menu Rendering
  window.renderRestaurantMenu = function (restaurantId, filterCategory = 'all') {
    const grid = document.getElementById('restaurant-food-grid');
    if (!grid) return;

    restaurantId = parseInt(restaurantId);
    let items = FOOD_ITEMS.filter(f => f.restaurantId === restaurantId);

    if (filterCategory !== 'all') {
      items = items.filter(f => {
        const cat = (f.category || '').toLowerCase();
        if (filterCategory === 'sides') return cat.includes('sides') || cat.includes('bbq') || cat === 'seafood';
        if (filterCategory === 'seafood') return cat === 'seafood' || cat.includes('sides');
        return cat === filterCategory.toLowerCase();
      });
    }

    if (items.length === 0) {
      grid.innerHTML = `
        <div style="grid-column: 1 / -1; text-align: center; padding: 3rem 1rem; background: #FFFFFF; border-radius: 16px; border: 1px dashed var(--border)">
          <div style="font-size: 2.5rem; margin-bottom: 0.5rem">🍽️</div>
          <h3 style="margin: 0 0 0.4rem; color: var(--text-main)">No dishes in this category</h3>
          <p class="meta">Please select another category tab above.</p>
        </div>
      `;
      return;
    }

    grid.innerHTML = items.map(item => {
      const currentQty = cart[item.id] || 0;
      const isAdded = currentQty > 0;

      return `
        <article class="modern-food-card group" data-category="${item.category}" data-id="${item.id}">
          <div class="card-image-wrap">
            <img 
              src="${item.image || getFoodItemImage(item.name, item.category)}" 
              alt="${item.name}" 
              class="card-food-img" 
              loading="lazy"
              onerror="this.onerror=null; this.src='https://images.unsplash.com/photo-1546069901-ba9599a7e63c?w=500&auto=format&fit=crop&q=60';"
            >
            <div class="image-overlay-gradient"></div>

            <div class="card-badge-top-left">
              <span class="rating-badge" title="${item.rating} out of 5 stars (${item.reviewsCount} reviews)">
                <svg width="12" height="12" viewBox="0 0 24 24" fill="#F59E0B" stroke="#F59E0B" stroke-width="1">
                  <polygon points="12 2 15.09 8.26 22 9.27 17 14.14 18.18 21.02 12 17.77 5.82 21.02 7 14.14 2 9.27 8.91 8.26 12 2"></polygon>
                </svg>
                <span>${item.rating}</span>
                <span class="rating-reviews-mini">(${item.reviewsCount})</span>
              </span>
            </div>

            <div class="card-badge-top-right">
              <span class="prep-time-badge" title="Estimated preparation and cooking time">
                <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round">
                  <circle cx="12" cy="12" r="10"></circle>
                  <polyline points="12 6 12 12 16 14"></polyline>
                </svg>
                <span>${item.prepTime}</span>
              </span>
            </div>

            ${item.badge ? `
              <div class="card-badge-bottom-left">
                <span class="feature-tag-chip ${item.isSpicy ? 'spicy' : ''}">${item.badge}</span>
              </div>
            ` : ''}
          </div>

          <div class="card-content-body">
            <div class="card-meta-line">
              <span class="card-restaurant-name">${item.restaurant}</span>
              <span class="meta-dot">&bull;</span>
              <span class="card-category-label">${capitalize(item.category)}</span>
            </div>

            <h3 class="card-dish-name" title="${item.name}">${item.name}</h3>
            
            <p class="card-dish-desc">${item.description}</p>

            <div class="card-footer-row">
              <div class="card-price-wrap">
                <span class="price-val">${formatRs(item.price)}</span>
              </div>

              <div class="cart-action-container" data-food-id="${item.id}">
                <button 
                  type="button" 
                  class="btn-add-cart ${isAdded ? 'hidden' : ''}" 
                  onclick="window.addToCart(${item.id})"
                  aria-label="Add ${item.name} to cart"
                >
                  <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round">
                    <line x1="12" y1="5" x2="12" y2="19"></line>
                    <line x1="5" y1="12" x2="19" y2="12"></line>
                  </svg>
                  <span>Add</span>
                </button>

                <div class="qty-control-group ${isAdded ? '' : 'hidden'}">
                  <button 
                    type="button" 
                    class="qty-btn qty-minus" 
                    onclick="window.changeQty(${item.id}, -1)" 
                    aria-label="Decrease quantity"
                  >
                    <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="3" stroke-linecap="round">
                      <line x1="5" y1="12" x2="19" y2="12"></line>
                    </svg>
                  </button>
                  <span class="qty-display">${currentQty}</span>
                  <button 
                    type="button" 
                    class="qty-btn qty-plus" 
                    onclick="window.changeQty(${item.id}, 1)" 
                    aria-label="Increase quantity"
                  >
                    <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="3" stroke-linecap="round">
                      <line x1="12" y1="5" x2="12" y2="19"></line>
                      <line x1="5" y1="12" x2="19" y2="12"></line>
                    </svg>
                  </button>
                </div>
              </div>
            </div>
          </div>
        </article>
      `;
    }).join('');
  };

  window.filterRestaurantCategory = function (categoryName) {
    const buttons = document.querySelectorAll('.restaurant-category-pill');
    buttons.forEach(btn => {
      const btnCat = btn.getAttribute('data-category') || 'all';
      if (btnCat.toLowerCase() === categoryName.toLowerCase()) {
        btn.classList.add('active');
      } else {
        btn.classList.remove('active');
      }
    });

    const grid = document.getElementById('restaurant-food-grid');
    if (grid) {
      const rid = grid.getAttribute('data-restaurant-id');
      grid.style.opacity = '0.4';
      grid.style.transform = 'scale(0.99)';
      setTimeout(() => {
        window.renderRestaurantMenu(rid, categoryName);
        grid.style.opacity = '1';
        grid.style.transform = 'scale(1)';
      }, 120);
    }
  };

  // Keyboard shortcut: Escape to close drawer / modal
  document.addEventListener('keydown', function (e) {
    if (e.key === 'Escape') {
      window.closeCartDrawer();
      window.closeCheckoutModal();
    }
  });

  // Initialization on DOM Ready
  document.addEventListener('DOMContentLoaded', function () {
    loadCart();
    window.renderFoodGrid('all');
    
    // Auto-render restaurant menu if on restaurant detail page
    const restGrid = document.getElementById('restaurant-food-grid');
    if (restGrid) {
      const rid = restGrid.getAttribute('data-restaurant-id');
      if (rid) {
        window.renderRestaurantMenu(rid, 'all');
      }
    }

    updateAllCartUI();
    setupAIConcierge();
    hookNavbarCart();
  });

})();
