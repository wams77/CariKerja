import com.google.firebase.firestore.PropertyName

data class Job(
    val id: String = "",
    val title: String = "",
    val company: String = "",
    val location: String = "",
    val category: String = "",
    val field: String = "Umum",
    @get:PropertyName("edu") @set:PropertyName("edu") var educationRequired: String = "",
    val description: String = "",
    val salary: String = "Tersedia",
    @get:PropertyName("type") @set:PropertyName("type") var jobType: String = "Full-time",
    @get:PropertyName("url") @set:PropertyName("url") var applyUrl: String = ""
)

data class UserProfile(
    val userId: String = "",
    val name: String = "",
    val education: String = "",
    val field: String = "Umum", // Bidang pilihan user
    val preferredLocation: String = "Indonesia",
    val skills: List<String> = emptyList(),
    val interestedCategories: List<String> = emptyList(),
    val bookmarkedJobIds: List<String> = emptyList(),
    val profileImageUrl: String? = null // Field baru untuk foto profil
)
