package com.carikerja.app

import androidx.lifecycle.ViewModel
import androidx.lifecycle.viewModelScope
import com.carikerja.app.data.FirebaseRepository
import com.carikerja.app.data.Job
import com.carikerja.app.data.ScraperService
import com.carikerja.app.data.UserProfile
import com.google.firebase.auth.FirebaseAuth
import com.google.firebase.auth.FirebaseUser
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.launch

class MainViewModel : ViewModel() {
    private val repository = FirebaseRepository()
    private val scraper = ScraperService()
    private val auth = FirebaseAuth.getInstance()

    private val _currentUser = MutableStateFlow<FirebaseUser?>(auth.currentUser)
    val currentUser: StateFlow<FirebaseUser?> = _currentUser

    private val _userProfile = MutableStateFlow<UserProfile?>(null)
    val userProfile: StateFlow<UserProfile?> = _userProfile

    private val _jobs = MutableStateFlow<List<Job>>(emptyList())
    val jobs: StateFlow<List<Job>> = _jobs

    private val _isLoading = MutableStateFlow(false)
    val isLoading: StateFlow<Boolean> = _isLoading

    private val _showOnlyBookmarks = MutableStateFlow(false)
    val showOnlyBookmarks: StateFlow<Boolean> = _showOnlyBookmarks

    init {
        auth.addAuthStateListener { firebaseAuth ->
            _currentUser.value = firebaseAuth.currentUser
            if (firebaseAuth.currentUser != null) {
                fetchUserProfile(firebaseAuth.currentUser!!.uid)
            } else {
                _userProfile.value = null
            }
        }
    }

    private fun fetchUserProfile(userId: String) {
        viewModelScope.launch {
            _isLoading.value = true
            val profile = repository.getUserProfile(userId)
            _userProfile.value = profile
            profile?.let { loadJobs(it.education) }
            _isLoading.value = false
        }
    }

    fun toggleShowBookmarks() {
        _showOnlyBookmarks.value = !_showOnlyBookmarks.value
    }

    fun logout() {
        auth.signOut()
    }

    fun refreshJobs() {
        viewModelScope.launch {
            _isLoading.value = true
            val fbJobs = repository.getAllJobs()
            val webJobs = scraper.scrapeJobsFromWeb()
            _jobs.value = fbJobs + webJobs
            _isLoading.value = false
        }
    }

    fun saveProfile(profile: UserProfile) {
        viewModelScope.launch {
            _isLoading.value = true
            repository.saveProfile(profile)
            _userProfile.value = profile
            loadJobs(profile.education)
            _isLoading.value = false
        }
    }

    fun toggleBookmark(jobId: String) {
        val currentProfile = _userProfile.value ?: return
        viewModelScope.launch {
            repository.toggleBookmark(currentProfile.userId, jobId)
            val newBookmarks = if (currentProfile.bookmarkedJobIds.contains(jobId)) {
                currentProfile.bookmarkedJobIds.filter { it != jobId }
            } else {
                currentProfile.bookmarkedJobIds + jobId
            }
            _userProfile.value = currentProfile.copy(bookmarkedJobIds = newBookmarks)
        }
    }

    private fun loadJobs(education: String) {
        viewModelScope.launch {
            _isLoading.value = true
            val matchingJobs = repository.getMatchingJobs(education)
            _jobs.value = matchingJobs
            _isLoading.value = false
        }
    }
}
