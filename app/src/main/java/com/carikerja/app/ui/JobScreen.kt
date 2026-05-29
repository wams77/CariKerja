package com.carikerja.app.ui

import android.content.Intent
import android.net.Uri
import androidx.compose.foundation.horizontalScroll
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.lazy.LazyColumn
import androidx.compose.foundation.lazy.items
import androidx.compose.foundation.rememberScrollState
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.automirrored.filled.ArrowBack
import androidx.compose.material.icons.automirrored.filled.ExitToApp
import androidx.compose.material.icons.filled.Favorite
import androidx.compose.material.icons.filled.FavoriteBorder
import androidx.compose.material3.*
import androidx.compose.runtime.Composable
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.platform.LocalContext
import androidx.compose.ui.unit.dp
import com.carikerja.app.data.Job

@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun JobScreen(
    jobs: List<Job>,
    bookmarkedIds: List<String>,
    showOnlyBookmarks: Boolean,
    selectedField: String,
    onBookmarkToggle: (String) -> Unit,
    onToggleFilter: () -> Unit,
    onFieldFilterSelected: (String) -> Unit,
    onBack: () -> Unit,
    onLogout: () -> Unit
) {
    val fields = listOf("Semua", "Informatika", "Ekonomi", "Teknik", "Kesehatan", "Hukum", "Sosial & Politik", "Sastra & Budaya", "Pendidikan")

    Column(
        modifier = Modifier
            .fillMaxSize()
            .padding(16.dp)
    ) {
        Row(
            modifier = Modifier.fillMaxWidth(),
            verticalAlignment = Alignment.CenterVertically
        ) {
            IconButton(onClick = onBack) {
                Icon(imageVector = Icons.AutoMirrored.Filled.ArrowBack, contentDescription = "Edit Profil")
            }
            Text(
                text = if (showOnlyBookmarks) "Simpanan" else "Lowongan",
                style = MaterialTheme.typography.headlineSmall,
                modifier = Modifier.weight(1f)
            )
            IconButton(onClick = onLogout) {
                Icon(imageVector = Icons.AutoMirrored.Filled.ExitToApp, contentDescription = "Logout", tint = MaterialTheme.colorScheme.error)
            }
            FilterChip(
                selected = showOnlyBookmarks,
                onClick = onToggleFilter,
                label = { Text("Bookmark") },
                leadingIcon = {
                    Icon(
                        imageVector = Icons.Default.Favorite,
                        contentDescription = null,
                        modifier = Modifier.size(FilterChipDefaults.IconSize)
                    )
                }
            )
        }
        
        Spacer(modifier = Modifier.height(8.dp))

        // Horizontal Category Filter
        Row(
            modifier = Modifier
                .fillMaxWidth()
                .horizontalScroll(rememberScrollState()),
            horizontalArrangement = Arrangement.spacedBy(8.dp)
        ) {
            fields.forEach { field ->
                FilterChip(
                    selected = selectedField == field,
                    onClick = { onFieldFilterSelected(field) },
                    label = { Text(field) }
                )
            }
        }

        Spacer(modifier = Modifier.height(8.dp))
        
        if (jobs.isEmpty()) {
            Box(modifier = Modifier.fillMaxSize(), contentAlignment = Alignment.Center) {
                Text(if (showOnlyBookmarks) "Belum ada simpanan" else "Tidak ada lowongan ditemukan")
            }
        } else {
            LazyColumn(verticalArrangement = Arrangement.spacedBy(8.dp)) {
                items(jobs) { job ->
                    JobItem(
                        job = job,
                        isBookmarked = bookmarkedIds.contains(job.id),
                        onBookmarkClick = { onBookmarkToggle(job.id) }
                    )
                }
            }
        }
    }
}

@Composable
fun JobItem(job: Job, isBookmarked: Boolean, onBookmarkClick: () -> Unit) {
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
                IconButton(onClick = onBookmarkClick) {
                    Icon(
                        imageVector = if (isBookmarked) Icons.Default.Favorite else Icons.Default.FavoriteBorder,
                        contentDescription = "Bookmark",
                        tint = if (isBookmarked) Color.Red else Color.Gray
                    )
                }
            }
            
            Row(verticalAlignment = Alignment.CenterVertically) {
                Text(
                    text = job.company, 
                    style = MaterialTheme.typography.bodyMedium, 
                    color = MaterialTheme.colorScheme.secondary,
                    modifier = Modifier.weight(1f)
                )
                Surface(
                    shape = MaterialTheme.shapes.small,
                    color = MaterialTheme.colorScheme.secondaryContainer
                ) {
                    Text(
                        text = job.field,
                        style = MaterialTheme.typography.labelSmall,
                        modifier = Modifier.padding(horizontal = 8.dp, vertical = 4.dp)
                    )
                }
                Spacer(modifier = Modifier.width(4.dp))
                Surface(
                    shape = MaterialTheme.shapes.small,
                    color = MaterialTheme.colorScheme.tertiaryContainer
                ) {
                    Text(
                        text = job.type,
                        style = MaterialTheme.typography.labelSmall,
                        modifier = Modifier.padding(horizontal = 8.dp, vertical = 4.dp)
                    )
                }
            }
            
            Spacer(modifier = Modifier.height(8.dp))
            
            Row {
                Text(text = "📍 ${job.location}", style = MaterialTheme.typography.bodySmall)
                Spacer(modifier = Modifier.width(12.dp))
                Text(text = "💰 ${job.salary}", style = MaterialTheme.typography.bodySmall)
            }

            Text(
                text = "🎓 Syarat: ${job.edu}",
                style = MaterialTheme.typography.bodySmall,
                color = MaterialTheme.colorScheme.primary,
                modifier = Modifier.padding(vertical = 4.dp)
            )
            
            HorizontalDivider(modifier = Modifier.padding(vertical = 8.dp))
            
            Button(
                onClick = {
                    if (job.url.isNotEmpty()) {
                        val intent = Intent(Intent.ACTION_VIEW, Uri.parse(job.url))
                        context.startActivity(intent)
                    }
                },
                modifier = Modifier.fillMaxWidth(),
                enabled = job.url.isNotEmpty()
            ) {
                Text("Daftar Sekarang")
            }
        }
    }
}
