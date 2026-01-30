/// User profile as returned by GET /api/v1/users/me
class UserProfile {
  final int id;
  final String email;
  final String username;
  final String? fullName;
  final int? age;
  final String? phone;
  final String? gender;
  final String? avatarUrl;
  final double? heightCm;
  final double? weightKg;
  final double? chestCm;
  final double? waistCm;
  final double? hipCm;
  final double? shoulderWidthCm;
  final String? preferredSize;

  const UserProfile({
    required this.id,
    required this.email,
    required this.username,
    this.fullName,
    this.age,
    this.phone,
    this.gender,
    this.avatarUrl,
    this.heightCm,
    this.weightKg,
    this.chestCm,
    this.waistCm,
    this.hipCm,
    this.shoulderWidthCm,
    this.preferredSize,
  });

  String get displayName => fullName?.trim().isNotEmpty == true ? fullName! : username;

  factory UserProfile.fromJson(Map<String, dynamic> json) {
    return UserProfile(
      id: (json['id'] as num).toInt(),
      email: json['email'] as String,
      username: json['username'] as String,
      fullName: json['full_name'] as String?,
      age: json['age'] != null ? (json['age'] as num).toInt() : null,
      phone: json['phone'] as String?,
      gender: json['gender'] as String?,
      avatarUrl: json['avatar_url'] as String?,
      heightCm: json['height_cm'] != null ? (json['height_cm'] as num).toDouble() : null,
      weightKg: json['weight_kg'] != null ? (json['weight_kg'] as num).toDouble() : null,
      chestCm: json['chest_cm'] != null ? (json['chest_cm'] as num).toDouble() : null,
      waistCm: json['waist_cm'] != null ? (json['waist_cm'] as num).toDouble() : null,
      hipCm: json['hip_cm'] != null ? (json['hip_cm'] as num).toDouble() : null,
      shoulderWidthCm: json['shoulder_width_cm'] != null ? (json['shoulder_width_cm'] as num).toDouble() : null,
      preferredSize: json['preferred_size'] as String?,
    );
  }

  Map<String, dynamic> toUpdateJson() {
    final map = <String, dynamic>{};
    if (fullName != null) map['full_name'] = fullName;
    if (age != null) map['age'] = age;
    if (phone != null) map['phone'] = phone;
    if (gender != null) map['gender'] = gender;
    if (heightCm != null) map['height_cm'] = heightCm;
    if (weightKg != null) map['weight_kg'] = weightKg;
    if (chestCm != null) map['chest_cm'] = chestCm;
    if (waistCm != null) map['waist_cm'] = waistCm;
    if (hipCm != null) map['hip_cm'] = hipCm;
    if (shoulderWidthCm != null) map['shoulder_width_cm'] = shoulderWidthCm;
    if (preferredSize != null) map['preferred_size'] = preferredSize;
    return map;
  }

  UserProfile copyWith({
    int? id,
    String? email,
    String? username,
    String? fullName,
    int? age,
    String? phone,
    String? gender,
    String? avatarUrl,
    double? heightCm,
    double? weightKg,
    double? chestCm,
    double? waistCm,
    double? hipCm,
    double? shoulderWidthCm,
    String? preferredSize,
  }) {
    return UserProfile(
      id: id ?? this.id,
      email: email ?? this.email,
      username: username ?? this.username,
      fullName: fullName ?? this.fullName,
      age: age ?? this.age,
      phone: phone ?? this.phone,
      gender: gender ?? this.gender,
      avatarUrl: avatarUrl ?? this.avatarUrl,
      heightCm: heightCm ?? this.heightCm,
      weightKg: weightKg ?? this.weightKg,
      chestCm: chestCm ?? this.chestCm,
      waistCm: waistCm ?? this.waistCm,
      hipCm: hipCm ?? this.hipCm,
      shoulderWidthCm: shoulderWidthCm ?? this.shoulderWidthCm,
      preferredSize: preferredSize ?? this.preferredSize,
    );
  }
}
