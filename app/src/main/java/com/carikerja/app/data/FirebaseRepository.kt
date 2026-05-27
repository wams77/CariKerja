package com.carikerja.app.data

import com.google.firebase.firestore.FirebaseFirestore
import kotlinx.coroutines.tasks.await

class FirebaseRepository {
    private val db = FirebaseFirestore.getInstance()

    suspend fun saveProfile(profile: UserProfile) {
        db.collection("users").document(profile.userId).set(profile).await()
    }

    suspend fun getMatchingJobs(education: String): List<Job> {
        return db.collection("jobs")
            .whereEqualTo("educationRequired", education)
            .get()
            .await()
            .toObjects(Job::class.java)
    }

    suspend fun getAllJobs(): List<Job> {
        return db.collection("jobs")
            .get()
            .await()
            .toObjects(Job::class.java)
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
