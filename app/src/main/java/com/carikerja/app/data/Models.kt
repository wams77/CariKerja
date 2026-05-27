package com.carikerja.app.data

data class Job(
    val id: String = "",
    val title: String = "",
    val company: String = "",
    val location: String = "",
    val category: String = "", // BUMN, BKN, Swasta, Luar Negeri
    val educationRequired: String = "",
    val description: String = ""
)

data class UserProfile(
    val userId: String = "",
    val name: String = "",
    val education: String = "", // e.g., "S1 Teknik Informatika"
    val skills: List<String> = emptyList(),
    val interestedCategories: List<String> = emptyList()
)
