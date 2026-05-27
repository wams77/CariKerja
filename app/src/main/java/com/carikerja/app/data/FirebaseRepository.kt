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
}
