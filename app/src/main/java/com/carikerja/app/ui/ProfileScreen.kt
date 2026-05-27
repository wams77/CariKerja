package com.carikerja.app.ui

import androidx.compose.foundation.layout.*
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Modifier
import androidx.compose.ui.unit.dp
import com.carikerja.app.data.UserProfile

@Composable
fun ProfileScreen(onSave: (UserProfile) -> Unit) {
    var name by remember { mutableStateOf("") }
    var education by remember { mutableStateOf("") }

    Column(
        modifier = Modifier
            .fillMaxSize()
            .padding(16.dp),
        verticalArrangement = Arrangement.spacedBy(8.dp)
    ) {
        Text("Lengkapi Profil Pencari Kerja", style = MaterialTheme.typography.headlineMedium)
        
        OutlinedTextField(
            value = name,
            onValueChange = { name = it },
            label = { Text("Nama Lengkap") },
            modifier = Modifier.fillMaxWidth()
        )

        OutlinedTextField(
            value = education,
            onValueChange = { education = it },
            label = { Text("Pendidikan Terakhir (contoh: S1 Teknik)") },
            modifier = Modifier.fillMaxWidth()
        )

        Button(
            onClick = {
                onSave(UserProfile(userId = "user_123", name = name, education = education))
            },
            modifier = Modifier.fillMaxWidth()
        ) {
            Text("Simpan Profil")
        }
    }
}
