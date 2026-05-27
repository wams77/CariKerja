package com.carikerja.app.data

data class Job(
    val id: String = "",
    val title: String = "",
    val company: String = "",
    val location: String = "",
    val category: String = "", // BUMN, BKN, Swasta, Luar Negeri
    val educationRequired: String = "",
    val description: String = "",
    val salary: String = "Tersedia", // Field baru
    val jobType: String = "Full-time", // Field baru (Full-time, Remote, dsb)
    val applyUrl: String = "" // Field baru untuk link pendaftaran
)

data class UserProfile(
    val userId: String = "",
    val name: String = "",
    val education: String = "",
    val preferredLocation: String = "Indonesia",
    val skills: List<String> = emptyList(),
    val interestedCategories: List<String> = emptyList(),
    val bookmarkedJobIds: List<String> = emptyList() // Field baru untuk simpan bookmark
)
