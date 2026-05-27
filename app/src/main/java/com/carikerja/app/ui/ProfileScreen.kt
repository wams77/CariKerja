package com.carikerja.app.ui

import androidx.compose.foundation.layout.*
import androidx.compose.foundation.rememberScrollState
import androidx.compose.foundation.verticalScroll
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.AccountCircle
import androidx.compose.material.icons.filled.Build
import androidx.compose.material.icons.filled.LocationOn
import androidx.compose.material.icons.filled.School
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.graphics.vector.ImageVector
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.dp
import com.carikerja.app.data.UserProfile

@Composable
fun ProfileScreen(onSave: (UserProfile) -> Unit) {
    var name by remember { mutableStateOf("") }
    var education by remember { mutableStateOf("") }
    var location by remember { mutableStateOf("Indonesia") }

    Column(
        modifier = Modifier
            .fillMaxSize()
            .padding(24.dp)
            .verticalScroll(rememberScrollState()),
        horizontalAlignment = Alignment.CenterHorizontally,
        verticalArrangement = Arrangement.spacedBy(16.dp)
    ) {
        Spacer(modifier = Modifier.height(32.dp))
        
        Icon(
            imageVector = Icons.Default.AccountCircle,
            contentDescription = null,
            modifier = Modifier.size(80.dp),
            tint = MaterialTheme.colorScheme.primary
        )
        
        Text(
            text = "Selamat Datang!",
            style = MaterialTheme.typography.headlineLarge,
            fontWeight = FontWeight.Bold
        )
        
        Text(
            text = "Lengkapi profil Anda agar kami dapat mencarikan lowongan yang paling sesuai.",
            style = MaterialTheme.typography.bodyMedium,
            color = MaterialTheme.colorScheme.onSurfaceVariant,
            textAlign = androidx.compose.ui.text.style.TextAlign.Center
        )

        Spacer(modifier = Modifier.height(16.dp))

        ProfileTextField(
            value = name,
            onValueChange = { name = it },
            label = "Nama Lengkap",
            icon = Icons.Default.AccountCircle,
            placeholder = "Masukkan nama lengkap Anda"
        )

        ProfileTextField(
            value = education,
            onValueChange = { education = it },
            label = "Pendidikan Terakhir",
            icon = Icons.Default.School,
            placeholder = "Contoh: S1 Teknik Informatika"
        )

        ProfileTextField(
            value = location,
            onValueChange = { location = it },
            label = "Lokasi Pilihan",
            icon = Icons.Default.LocationOn,
            placeholder = "Contoh: Jakarta atau Remote"
        )

        Spacer(modifier = Modifier.height(24.dp))

        Button(
            onClick = {
                if (name.isNotBlank() && education.isNotBlank()) {
                    onSave(UserProfile(
                        userId = "user_" + System.currentTimeMillis(), 
                        name = name, 
                        education = education,
                        preferredLocation = location
                    ))
                }
            },
            modifier = Modifier
                .fillMaxWidth()
                .height(56.dp),
            shape = MaterialTheme.shapes.medium
        ) {
            Text("Mulai Cari Kerja", style = MaterialTheme.typography.titleMedium)
        }
    }
}

@Composable
fun ProfileTextField(
    value: String,
    onValueChange: (String) -> Unit,
    label: String,
    icon: ImageVector,
    placeholder: String
) {
    OutlinedTextField(
        value = value,
        onValueChange = onValueChange,
        label = { Text(label) },
        placeholder = { Text(placeholder) },
        leadingIcon = { Icon(imageVector = icon, contentDescription = null) },
        modifier = Modifier.fillMaxWidth(),
        singleLine = true,
        shape = MaterialTheme.shapes.medium
    )
}
