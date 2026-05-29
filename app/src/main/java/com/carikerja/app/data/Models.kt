package com.carikerja.app.data

data class Job(
    var id: String = "",
    var title: String = "",
    var company: String = "",
    var location: String = "",
    var category: String = "",
    var field: String = "Umum",
    var edu: String = "",       // Sesuaikan dengan Firestore
    var description: String = "",
    var salary: String = "Tersedia",
    var type: String = "Full-time", // Sesuaikan dengan Firestore
    var url: String = ""        // Sesuaikan dengan Firestore
)

data class UserProfile(
    val userId: String = "",
    val name: String = "",
    val education: String = "",
    val field: String = "Umum",
    val preferredLocation: String = "Indonesia",
    val profileImageUrl: String? = null,
    val bookmarkedJobIds: List<String> = emptyList()
)
