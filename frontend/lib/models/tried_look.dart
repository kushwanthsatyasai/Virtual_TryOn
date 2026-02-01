/// A single virtual try-on result (for Recent Looks).
class TriedLook {
  final int id;
  final String resultImageUrl;
  final String? clothImageUrl;
  final String? createdAt;
  final TriedLookMetadata? metadata;

  const TriedLook({
    required this.id,
    required this.resultImageUrl,
    this.clothImageUrl,
    this.createdAt,
    this.metadata,
  });

  factory TriedLook.fromJson(Map<String, dynamic> json, String baseUrl) {
    final resultPath = json['result_image_url'] as String? ?? '';
    final clothPath = json['cloth_image_url'] as String?;
    final resultUrl = resultPath.startsWith('http') ? resultPath : '$baseUrl$resultPath';
    final clothUrl = clothPath != null && clothPath.isNotEmpty
        ? (clothPath.startsWith('http') ? clothPath : '$baseUrl$clothPath')
        : null;
    final meta = json['metadata'] as Map<String, dynamic>?;
    return TriedLook(
      id: json['id'] as int,
      resultImageUrl: resultUrl,
      clothImageUrl: clothUrl,
      createdAt: json['created_at'] as String?,
      metadata: meta != null && meta.isNotEmpty ? TriedLookMetadata.fromJson(meta) : null,
    );
  }
}

class TriedLookMetadata {
  final String? productId;
  final String? productName;
  final String? productImageUrl;

  const TriedLookMetadata({
    this.productId,
    this.productName,
    this.productImageUrl,
  });

  factory TriedLookMetadata.fromJson(Map<String, dynamic> json) {
    return TriedLookMetadata(
      productId: json['product_id'] as String?,
      productName: json['product_name'] as String?,
      productImageUrl: json['product_image_url'] as String?,
    );
  }
}
