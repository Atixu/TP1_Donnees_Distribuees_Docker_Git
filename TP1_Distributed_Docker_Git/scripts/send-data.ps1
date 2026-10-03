param(
  [string]$Key = "product-001",
  [string]$Value = "Produit A"
)

$body = @{ key = $Key; value = $Value } | ConvertTo-Json

Write-Host "==> Leader"
Invoke-RestMethod -Method Post -Uri http://localhost:8080/data -ContentType "application/json" -Body $body

Write-Host "==> Follower 1 (simulation de réplication)"
Invoke-RestMethod -Method Post -Uri http://localhost:8081/data -ContentType "application/json" -Body $body

Write-Host "==> Follower 2 (simulation de réplication)"
Invoke-RestMethod -Method Post -Uri http://localhost:8082/data -ContentType "application/json" -Body $body

Write-Host "`n==> Vérification"
Invoke-RestMethod http://localhost:8080/data
Invoke-RestMethod http://localhost:8081/data
Invoke-RestMethod http://localhost:8082/data
