package com.carikerja.app

import android.os.Bundle
import androidx.activity.ComponentActivity
import androidx.activity.compose.setContent
import androidx.activity.enableEdgeToEdge
import androidx.compose.foundation.layout.Box
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.layout.padding
import androidx.compose.material3.Scaffold
import androidx.compose.runtime.collectAsState
import androidx.compose.runtime.getValue
import androidx.compose.ui.Modifier
import androidx.lifecycle.viewmodel.compose.viewModel
import com.carikerja.app.ui.JobScreen
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
                val userProfile by viewModel.userProfile.collectAsState()
                val jobs by viewModel.jobs.collectAsState()

                Scaffold(
                    modifier = Modifier.fillMaxSize(),
                    floatingActionButton = {
                        if (userProfile != null) {
                            androidx.compose.material3.FloatingActionButton(onClick = { viewModel.refreshJobs() }) {
                                androidx.compose.material3.Text("Cek Lowongan Baru")
                            }
                        }
                    }
                ) { innerPadding ->
                    Box(modifier = Modifier.padding(innerPadding)) {
                        if (userProfile == null) {
                            ProfileScreen(onSave = { viewModel.saveProfile(it) })
                        } else {
                            JobScreen(jobs = jobs)
                        }
                    }
                }
            }
        }
    }
}
