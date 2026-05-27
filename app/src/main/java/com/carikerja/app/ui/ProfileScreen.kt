package com.carikerja.app.ui

import androidx.compose.foundation.layout.*
import androidx.compose.foundation.rememberScrollState
import androidx.compose.foundation.verticalScroll
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.*
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.graphics.vector.ImageVector
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.dp
import com.carikerja.app.data.UserProfile

@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun ProfileScreen(onSave: (UserProfile) -> Unit) {
    var name by remember { mutableStateOf("") }
    var education by remember { mutableStateOf("") }
    var location by remember { mutableStateOf("Indonesia") }
    var selectedField by remember { mutableStateOf("Umum") }
    var expanded by remember { mutableStateOf(false) }
    
    val fields = listOf("Umum", "Informatika", "Ekonomi", "Teknik", "Kesehatan", "Hukum", "Sosial & Politik", "Sastra & Budaya", "Pendidikan")

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
        
        Text(text = "Lengkapi Profil", style = MaterialTheme.typography.headlineLarge, fontWeight = FontWeight.Bold)

        ProfileTextField(value = name, onValueChange = { name = it }, label = "Nama Lengkap", icon = Icons.Default.Person, placeholder = "Nama Anda")
        ProfileTextField(value = education, onValueChange = { education = it }, label = "Pendidikan Terakhir", icon = Icons.Default.School, placeholder = "Contoh: S1 Teknik")
        ProfileTextField(value = location, onValueChange = { location = it }, label = "Lokasi Pilihan", icon = Icons.Default.LocationOn, placeholder = "Contoh: Jakarta / Remote")

        // Bidang Kategori Dropdown
        ExposedDropdownMenuBox(
            expanded = expanded,
            onExpandedChange = { expanded = !expanded },
            modifier = Modifier.fillMaxWidth()
        ) {
            OutlinedTextField(
                value = selectedField,
                onValueChange = {},
                readOnly = true,
                label = { Text("Bidang Keahlian") },
                leadingIcon = { Icon(Icons.Default.Build, contentDescription = null) },
                trailingIcon = { ExposedDropdownMenuDefaults.TrailingIcon(expanded = expanded) },
                modifier = Modifier.menuAnchor().fillMaxWidth(),
                shape = MaterialTheme.shapes.medium
            )
            ExposedDropdownMenu(
                expanded = expanded,
                onDismissRequest = { expanded = false }
            ) {
                fields.forEach { field ->
                    DropdownMenuItem(
                        text = { Text(field) },
                        onClick = {
                            selectedField = field
                            expanded = false
                        }
                    )
                }
            }
        }

        Spacer(modifier = Modifier.height(24.dp))

        Button(
            onClick = {
                if (name.isNotBlank()) {
                    onSave(UserProfile(
                        userId = "", // Handled by ViewModel
                        name = name, 
                        education = education,
                        field = selectedField,
                        preferredLocation = location
                    ))
                }
            },
            modifier = Modifier.fillMaxWidth().height(56.dp),
            shape = MaterialTheme.shapes.medium
        ) {
            Text("Mulai Cari Kerja", style = MaterialTheme.typography.titleMedium)
        }
    }
}

@Composable
fun ProfileTextField(value: String, onValueChange: (String) -> Unit, label: String, icon: ImageVector, placeholder: String) {
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
