package com.carikerja.app

import android.os.Bundle
import androidx.activity.ComponentActivity
import androidx.activity.compose.setContent
import androidx.activity.enableEdgeToEdge
import androidx.compose.foundation.layout.Box
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.layout.padding
import androidx.compose.material3.CircularProgressIndicator
import androidx.compose.material3.Scaffold
import androidx.compose.runtime.collectAsState
import androidx.compose.runtime.getValue
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.unit.dp
import androidx.lifecycle.viewmodel.compose.viewModel
import com.carikerja.app.ui.JobScreen
import com.carikerja.app.ui.LoginScreen
import com.carikerja.app.ui.ProfileScreen
import com.carikerja.app.ui.theme.CariKerjaTheme
import com.google.firebase.messaging.FirebaseMessaging

class MainActivity : ComponentActivity() {
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        
        // Berlangganan topik agar menerima notifikasi dari Bot
        FirebaseMessaging.getInstance().subscribeToTopic("lowongan")

        enableEdgeToEdge()
        setContent {
            CariKerjaTheme {
                val viewModel: MainViewModel = viewModel()
                val currentUser by viewModel.currentUser.collectAsState()
                val userProfile by viewModel.userProfile.collectAsState()
                val jobs by viewModel.jobs.collectAsState()
                val isLoading by viewModel.isLoading.collectAsState()
                val showOnlyBookmarks by viewModel.showOnlyBookmarks.collectAsState()

                Scaffold(
                    modifier = Modifier.fillMaxSize(),
                    floatingActionButton = {
                        if (currentUser != null && userProfile != null && !isLoading) {
                            androidx.compose.material3.FloatingActionButton(onClick = { viewModel.refreshJobs() }) {
                                androidx.compose.material3.Text("Cek Lowongan Baru", modifier = Modifier.padding(horizontal = 16.dp))
                            }
                        }
                    }
                ) { innerPadding ->
                    Box(modifier = Modifier.padding(innerPadding)) {
                        when {
                            isLoading -> {
                                Box(modifier = Modifier.fillMaxSize(), contentAlignment = Alignment.Center) {
                                    CircularProgressIndicator()
                                }
                            }
                            currentUser == null -> {
                                LoginScreen()
                            }
                            userProfile == null -> {
                                ProfileScreen(onSave = { 
                                    val profileWithId = it.copy(userId = currentUser!!.uid)
                                    viewModel.saveProfile(profileWithId) 
                                })
                            }
                            else -> {
                                JobScreen(
                                    jobs = jobs,
                                    bookmarkedIds = userProfile?.bookmarkedJobIds ?: emptyList(),
                                    showOnlyBookmarks = showOnlyBookmarks,
                                    onBookmarkToggle = { viewModel.toggleBookmark(it) },
                                    onToggleFilter = { viewModel.toggleShowBookmarks() },
                                    onBack = { viewModel.logout() }
                                )
                            }
                        }
                    }
                }
            }
        }
    }
}
