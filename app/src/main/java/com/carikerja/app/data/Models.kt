package com.carikerja.app.data

data class Job(
    val id: String = "",
    val title: String = "",
    val company: String = "",
    val location: String = "",
    val category: String = "", // BUMN, CPNS, Luar Negeri, dsb
    val field: String = "Umum", // Bidang: Informatika, Ekonomi, Teknik, Umum
    val educationRequired: String = "",
    val description: String = "",
    val salary: String = "Tersedia",
    val jobType: String = "Full-time",
    val applyUrl: String = ""
)

data class UserProfile(
    val userId: String = "",
    val name: String = "",
    val education: String = "",
    val field: String = "Umum", // Bidang pilihan user
    val preferredLocation: String = "Indonesia",
    val skills: List<String> = emptyList(),
    val interestedCategories: List<String> = emptyList(),
    val bookmarkedJobIds: List<String> = emptyList()
)
