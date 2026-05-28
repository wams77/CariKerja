package com.carikerja.app.data

import com.google.firebase.firestore.FirebaseFirestore
import com.google.firebase.storage.FirebaseStorage
import kotlinx.coroutines.tasks.await
import java.io.ByteArrayOutputStream

class FirebaseRepository {
    private val db = FirebaseFirestore.getInstance()
    private val storage = FirebaseStorage.getInstance()

    suspend fun saveProfile(profile: UserProfile) {
        db.collection("users").document(profile.userId).set(profile).await()
    }

    suspend fun getUserProfile(userId: String): UserProfile? {
        return db.collection("users").document(userId).get().await().toObject(UserProfile::class.java)
    }

    suspend fun uploadProfileImage(userId: String, imageBytes: ByteArray): String {
        val storageRef = storage.reference.child("profile_images/$userId.jpg")
        storageRef.putBytes(imageBytes).await()
        return storageRef.downloadUrl.await().toString()
    }

    suspend fun getMatchingJobs(education: String): List<Job> {
        val allJobs = getAllJobs()
        // Filter cerdas: Ambil yang cocok dengan jurusan ATAU yang untuk semua jurusan
        return allJobs.filter { 
            it.educationRequired.contains(education, ignoreCase = true) || 
            it.educationRequired.contains("Semua Jurusan", ignoreCase = true) ||
            it.educationRequired == "Semua Jenjang"
        }
    }

    suspend fun getAllJobs(): List<Job> {
        val snapshot = db.collection("jobs").get().await()
        return snapshot.documents.mapNotNull { doc ->
            val job = doc.toObject(Job::class.java)
            job?.copy(id = doc.id) // Mengambil ID dari nama dokumen Firebase
        }
    }

    suspend fun toggleBookmark(userId: String, jobId: String) {
        val userRef = db.collection("users").document(userId)
        val user = userRef.get().await().toObject(UserProfile::class.java) ?: return
        
        val newBookmarks = if (user.bookmarkedJobIds.contains(jobId)) {
            user.bookmarkedJobIds.filter { it != jobId }
        } else {
            user.bookmarkedJobIds + jobId
        }
        
        userRef.update("bookmarkedJobIds", newBookmarks).await()
    }
}
