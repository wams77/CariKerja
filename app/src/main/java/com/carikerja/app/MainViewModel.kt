package com.carikerja.app

import androidx.lifecycle.ViewModel
import androidx.lifecycle.viewModelScope
import com.carikerja.app.data.FirebaseRepository
import com.carikerja.app.data.Job
import com.carikerja.app.data.ScraperService
import com.carikerja.app.data.UserProfile
import com.google.firebase.auth.FirebaseAuth
import com.google.firebase.auth.FirebaseUser
import kotlinx.coroutines.flow.*
import kotlinx.coroutines.launch

class MainViewModel : ViewModel() {
    private val repository = FirebaseRepository()
    private val scraper = ScraperService()
    private val auth = FirebaseAuth.getInstance()

    private val _currentUser = MutableStateFlow<FirebaseUser?>(auth.currentUser)
    val currentUser: StateFlow<FirebaseUser?> = _currentUser

    private val _userProfile = MutableStateFlow<UserProfile?>(null)
    val userProfile: StateFlow<UserProfile?> = _userProfile

    private val _allJobs = MutableStateFlow<List<Job>>(emptyList())
    
    private val _isLoading = MutableStateFlow(false)
    val isLoading: StateFlow<Boolean> = _isLoading

    private val _showOnlyBookmarks = MutableStateFlow(false)
    val showOnlyBookmarks: StateFlow<Boolean> = _showOnlyBookmarks

    private val _selectedFieldFilter = MutableStateFlow("Semua")
    val selectedFieldFilter: StateFlow<String> = _selectedFieldFilter

    val filteredJobs: StateFlow<List<Job>> = combine(_allJobs, _showOnlyBookmarks, _selectedFieldFilter, _userProfile) { 
        jobs, showBookmarks, fieldFilter, profile ->
        
        var filtered = jobs
        
        if (showBookmarks && profile != null) {
            filtered = filtered.filter { profile.bookmarkedJobIds.contains(it.id) }
        }
        
        if (fieldFilter != "Semua") {
            filtered = filtered.filter { 
                it.field.contains(fieldFilter, ignoreCase = true) || it.field == "Umum" 
            }
        }
        
        filtered
    }.stateIn(viewModelScope, SharingStarted.WhileSubscribed(5000), emptyList())

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
            profile?.let { 
                _selectedFieldFilter.value = it.field
                refreshJobs() 
            }
            _isLoading.value = false
        }
    }

    fun setFieldFilter(field: String) {
        _selectedFieldFilter.value = field
    }

    fun toggleShowBookmarks() {
        _showOnlyBookmarks.value = !_showOnlyBookmarks.value
    }

    fun editProfile() {
        // Hanya menghapus data profil di tampilan agar user bisa input ulang
        // Tanpa melakukan auth.signOut()
        _userProfile.value = null
    }

    fun logout() {
        auth.signOut()
    }

    fun refreshJobs() {
        viewModelScope.launch {
            _isLoading.value = true
            val fbJobs = repository.getAllJobs()
            val webJobs = scraper.scrapeJobsFromWeb()
            _allJobs.value = fbJobs + webJobs
            _isLoading.value = false
        }
    }

    fun saveProfile(profile: UserProfile) {
        viewModelScope.launch {
            _isLoading.value = true
            repository.saveProfile(profile)
            _userProfile.value = profile
            _selectedFieldFilter.value = profile.field
            refreshJobs()
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
}
