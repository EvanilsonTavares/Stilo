# Stilo - Secret Setup Script for GCP
# Este script ajuda a criar os segredos no Google Cloud Secret Manager

$SECRETS = @(
    "GEMINI_API_KEY",
    "WHATSAPP_ACCESS_TOKEN",
    "WHATSAPP_VERIFY_TOKEN",
    "WHATSAPP_APP_SECRET",
    "REPLICATE_API_TOKEN"
)

Write-Host "--- Configurando Segredos no GCP ---" -ForegroundColor Cyan

foreach ($name in $SECRETS) {
    $exists = gcloud secrets list --filter="name ~ $name" --format="value(name)"
    
    if (-not $exists) {
        Write-Host "Criando segredo: $name"
        gcloud secrets create $name --replication-policy="automatic"
    } else {
        Write-Host "Segredo $name já existe."
    }
    
    # Pergunta o valor se não quiser ler do .env (opcional)
    # Por agora, este script apenas garante que eles existam.
}

Write-Host "`nSegredos criados com sucesso! Não esqueça de adicionar as versões com seus valores reais." -ForegroundColor Green
Write-Host "Comando exemplo: echo 'seu-valor' | gcloud secrets versions add GEMINI_API_KEY --data-file=-"
