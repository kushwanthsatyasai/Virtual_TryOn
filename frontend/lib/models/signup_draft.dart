class SignupDraft {
  SignupDraft({
    required this.name,
    required this.age,
    required this.phone,
    required this.email,
    required this.gender,
    required this.password,
    this.chestIn,
    this.waistIn,
    this.heightFeet,
    this.heightInches,
    this.weightLbs,
  });

  final String name;
  final int age;
  final String phone;
  final String email;
  final String gender;
  final String password;

  // Optional measurements (user can skip)
  final double? chestIn;
  final double? waistIn;
  final int? heightFeet;
  final int? heightInches;
  final double? weightLbs;

  SignupDraft copyWith({
    String? name,
    int? age,
    String? phone,
    String? email,
    String? gender,
    String? password,
    double? chestIn,
    double? waistIn,
    int? heightFeet,
    int? heightInches,
    double? weightLbs,
    bool clearMeasurements = false,
  }) {
    return SignupDraft(
      name: name ?? this.name,
      age: age ?? this.age,
      phone: phone ?? this.phone,
      email: email ?? this.email,
      gender: gender ?? this.gender,
      password: password ?? this.password,
      chestIn: clearMeasurements ? null : (chestIn ?? this.chestIn),
      waistIn: clearMeasurements ? null : (waistIn ?? this.waistIn),
      heightFeet: clearMeasurements ? null : (heightFeet ?? this.heightFeet),
      heightInches: clearMeasurements ? null : (heightInches ?? this.heightInches),
      weightLbs: clearMeasurements ? null : (weightLbs ?? this.weightLbs),
    );
  }

  bool get hasMeasurements =>
      chestIn != null && waistIn != null && heightFeet != null && heightInches != null && weightLbs != null;

  Map<String, dynamic> toRegisterPayload() {
    final payload = <String, dynamic>{
      // Backend accepts either "name" or "full_name"
      'name': name,
      'age': age,
      'phone': phone,
      'email': email,
      'gender': gender,
      'password': password,
    };

    if (hasMeasurements) {
      // Convert imperial -> metric for backend DB columns
      final heightTotalIn = (heightFeet! * 12) + heightInches!;
      final heightCm = heightTotalIn * 2.54;
      final weightKg = weightLbs! * 0.45359237;
      final chestCm = chestIn! * 2.54;
      final waistCm = waistIn! * 2.54;

      payload['height_cm'] = double.parse(heightCm.toStringAsFixed(2));
      payload['weight_kg'] = double.parse(weightKg.toStringAsFixed(2));
      payload['chest_cm'] = double.parse(chestCm.toStringAsFixed(2));
      payload['waist_cm'] = double.parse(waistCm.toStringAsFixed(2));
    }

    return payload;
  }
}

