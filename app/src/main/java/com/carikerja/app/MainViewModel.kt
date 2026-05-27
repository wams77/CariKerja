package com.carikerja.app

import androidx.lifecycle.ViewModel
import androidx.lifecycle.viewModelScope
import com.carikerja.app.data.FirebaseRepository
import com.carikerja.app.data.Job
import com.carikerja.app.data.ScraperService
import com.carikerja.app.data.UserProfile
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.launch

class MainViewModel : ViewModel() {
    private val repository = FirebaseRepository()
    private val scraper = ScraperService()

    private val _userProfile = MutableStateFlow<UserProfile?>(null)
    val userProfile: StateFlow<UserProfile?> = _userProfile

    private val _jobs = MutableStateFlow<List<Job>>(emptyList())
    val jobs: StateFlow<List<Job>> = _jobs

    private val _showOnlyBookmarks = MutableStateFlow(false)
    val showOnlyBookmarks: StateFlow<Boolean> = _showOnlyBookmarks

    fun toggleShowBookmarks() {
        _showOnlyBookmarks.value = !_showOnlyBookmarks.value
    }

    fun refreshJobs() {
        viewModelScope.launch {
            val fbJobs = repository.getAllJobs()
            val webJobs = scraper.scrapeJobsFromWeb()
            _jobs.value = fbJobs + webJobs
        }
    }

    fun saveProfile(profile: UserProfile) {
        viewModelScope.launch {
            repository.saveProfile(profile)
            _userProfile.value = profile
            loadJobs(profile.education)
        }
    }

    fun toggleBookmark(jobId: String) {
        val currentProfile = _userProfile.value ?: return
        viewModelScope.launch {
            repository.toggleBookmark(currentProfile.userId, jobId)
            // Update local state
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
            val matchingJobs = repository.getMatchingJobs(education)
            _jobs.value = matchingJobs
        }
    }
}
