class ProductItem {
  final String name;
  final double price;
  final String imageUrl;
  /// Garment from a third-party API (e.g. FakeStore); try-on uses the image URL.
  final bool isExternalCatalog;

  const ProductItem({
    required this.name,
    required this.price,
    required this.imageUrl,
    this.isExternalCatalog = false,
  });
}
