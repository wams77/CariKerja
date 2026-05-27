package com.carikerja.app.ui

import android.content.Intent
import android.net.Uri
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.lazy.LazyColumn
import androidx.compose.foundation.lazy.items
import androidx.compose.material3.*
import androidx.compose.runtime.Composable
import androidx.compose.ui.Modifier
import androidx.compose.ui.platform.LocalContext
import androidx.compose.ui.unit.dp
import com.carikerja.app.data.Job

@Composable
fun JobScreen(jobs: List<Job>) {
    Column(
        modifier = Modifier
            .fillMaxSize()
            .padding(16.dp)
    ) {
        Text("Lowongan Tersedia", style = MaterialTheme.typography.headlineMedium)
        Spacer(modifier = Modifier.height(8.dp))
        
        LazyColumn(verticalArrangement = Arrangement.spacedBy(8.dp)) {
            items(jobs) { job ->
                JobItem(job)
            }
        }
    }
}

@Composable
fun JobItem(job: Job) {
    val context = LocalContext.current
    Card(
        modifier = Modifier.fillMaxWidth(),
        elevation = CardDefaults.cardElevation(defaultElevation = 2.dp)
    ) {
        Column(modifier = Modifier.padding(16.dp)) {
            Row(
                modifier = Modifier.fillMaxWidth(),
                horizontalArrangement = Arrangement.SpaceBetween
            ) {
                Text(
                    text = job.title, 
                    style = MaterialTheme.typography.titleLarge, 
                    modifier = Modifier.weight(1f)
                )
                Surface(
                    shape = MaterialTheme.shapes.small,
                    color = MaterialTheme.colorScheme.secondaryContainer
                ) {
                    Text(
                        text = job.jobType,
                        style = MaterialTheme.typography.labelSmall,
                        modifier = Modifier.padding(horizontal = 8.dp, vertical = 4.dp)
                    )
                }
            }
            
            Text(
                text = job.company, 
                style = MaterialTheme.typography.bodyMedium, 
                color = MaterialTheme.colorScheme.secondary
            )
            
            Spacer(modifier = Modifier.height(8.dp))
            
            Row {
                Text(text = "📍 ${job.location}", style = MaterialTheme.typography.bodySmall)
                Spacer(modifier = Modifier.width(12.dp))
                Text(text = "💰 ${job.salary}", style = MaterialTheme.typography.bodySmall)
            }

            Text(
                text = "🎓 Syarat: ${job.educationRequired}",
                style = MaterialTheme.typography.bodySmall,
                color = MaterialTheme.colorScheme.primary,
                modifier = Modifier.padding(vertical = 4.dp)
            )
            
            HorizontalDivider(modifier = Modifier.padding(vertical = 8.dp))
            
            Button(
                onClick = {
                    if (job.applyUrl.isNotEmpty()) {
                        val intent = Intent(Intent.ACTION_VIEW, Uri.parse(job.applyUrl))
                        context.startActivity(intent)
                    }
                },
                modifier = Modifier.fillMaxWidth(),
                enabled = job.applyUrl.isNotEmpty()
            ) {
                Text("Daftar Sekarang")
            }
        }
    }
}
