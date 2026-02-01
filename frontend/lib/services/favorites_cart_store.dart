import 'dart:convert';

import 'package:flutter/foundation.dart';
import 'package:shared_preferences/shared_preferences.dart';

/// Item in Favorites (same shape as product for display).
class FavoriteItem {
  final String name;
  final double price;
  final String imageUrl;

  const FavoriteItem({
    required this.name,
    required this.price,
    required this.imageUrl,
  });

  Map<String, dynamic> toJson() => {'name': name, 'price': price, 'imageUrl': imageUrl};

  static FavoriteItem fromJson(Map<String, dynamic> j) => FavoriteItem(
        name: j['name'] as String? ?? '',
        price: (j['price'] as num?)?.toDouble() ?? 0,
        imageUrl: j['imageUrl'] as String? ?? '',
      );
}

/// Item in Cart (includes size and quantity).
class CartItem {
  final String name;
  final String size;
  final double price;
  final String imageUrl;
  int quantity;

  CartItem({
    required this.name,
    required this.size,
    required this.price,
    required this.imageUrl,
    this.quantity = 1,
  });

  Map<String, dynamic> toJson() => {
        'name': name,
        'size': size,
        'price': price,
        'imageUrl': imageUrl,
        'quantity': quantity,
      };

  static CartItem fromJson(Map<String, dynamic> j) => CartItem(
        name: j['name'] as String? ?? '',
        size: j['size'] as String? ?? 'M',
        price: (j['price'] as num?)?.toDouble() ?? 0,
        imageUrl: j['imageUrl'] as String? ?? '',
        quantity: j['quantity'] as int? ?? 1,
      );
}

const _favoritesKey = 'favorites_cart_favorites';
const _cartKey = 'favorites_cart_cart';

/// Global store for favorites and cart. Persisted to SharedPreferences so data
/// survives logout and app restarts.
class FavoritesCartStore {
  FavoritesCartStore._();

  static final List<FavoriteItem> _favorites = [];
  static final List<CartItem> _cart = [];
  static bool _loaded = false;

  static final ValueNotifier<int> favoritesCount = ValueNotifier(0);
  static final ValueNotifier<int> cartCount = ValueNotifier(0);

  static List<FavoriteItem> get favorites => List.unmodifiable(_favorites);
  static List<CartItem> get cartItems => List.from(_cart);

  /// Load persisted favorites and cart from disk. Call once at app start (e.g. main).
  static Future<void> loadFromDisk() async {
    if (_loaded) return;
    _loaded = true;
    try {
      final prefs = await SharedPreferences.getInstance();
      final favJson = prefs.getString(_favoritesKey);
      if (favJson != null && favJson.isNotEmpty) {
        final list = jsonDecode(favJson) as List<dynamic>?;
        if (list != null) {
          _favorites.clear();
          for (final e in list) {
            if (e is Map<String, dynamic>) _favorites.add(FavoriteItem.fromJson(e));
          }
          favoritesCount.value = _favorites.length;
        }
      }
      final cartJson = prefs.getString(_cartKey);
      if (cartJson != null && cartJson.isNotEmpty) {
        final list = jsonDecode(cartJson) as List<dynamic>?;
        if (list != null) {
          _cart.clear();
          for (final e in list) {
            if (e is Map<String, dynamic>) _cart.add(CartItem.fromJson(e));
          }
          _updateCartCount();
        }
      }
    } catch (_) {}
  }

  static Future<void> _saveFavorites() async {
    try {
      final prefs = await SharedPreferences.getInstance();
      final list = _favorites.map((e) => e.toJson()).toList();
      await prefs.setString(_favoritesKey, jsonEncode(list));
    } catch (_) {}
  }

  static Future<void> _saveCart() async {
    try {
      final prefs = await SharedPreferences.getInstance();
      final list = _cart.map((e) => e.toJson()).toList();
      await prefs.setString(_cartKey, jsonEncode(list));
    } catch (_) {}
  }

  static void addFavorite(FavoriteItem item) {
    if (_favorites.any((e) => e.name == item.name && e.imageUrl == item.imageUrl)) return;
    _favorites.add(item);
    favoritesCount.value = _favorites.length;
    _saveFavorites();
  }

  static void removeFavoriteAt(int index) {
    if (index >= 0 && index < _favorites.length) {
      _favorites.removeAt(index);
      favoritesCount.value = _favorites.length;
      _saveFavorites();
    }
  }

  static bool isFavorite(String name, String imageUrl) {
    return _favorites.any((e) => e.name == name && e.imageUrl == imageUrl);
  }

  static void addToCart(CartItem item) {
    final i = _cart.indexWhere((e) => e.name == item.name && e.size == item.size);
    if (i >= 0) {
      _cart[i].quantity += item.quantity;
    } else {
      _cart.add(CartItem(
        name: item.name,
        size: item.size,
        price: item.price,
        imageUrl: item.imageUrl,
        quantity: item.quantity,
      ));
    }
    _updateCartCount();
    _saveCart();
  }

  static void updateCartQuantity(int index, int delta) {
    if (index < 0 || index >= _cart.length) return;
    final q = _cart[index].quantity + delta;
    if (q <= 0) {
      _cart.removeAt(index);
    } else {
      _cart[index].quantity = q;
    }
    _updateCartCount();
    _saveCart();
  }

  static void removeCartItemAt(int index) {
    if (index >= 0 && index < _cart.length) {
      _cart.removeAt(index);
      _updateCartCount();
      _saveCart();
    }
  }

  static void _updateCartCount() {
    cartCount.value = _cart.fold(0, (sum, e) => sum + e.quantity);
  }
}
