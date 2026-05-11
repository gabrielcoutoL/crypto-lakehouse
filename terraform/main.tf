provider "aws" {
    region = "us-east-1"
}

#CRIANDO CAMADA BRONZE NO S3
resource "aws_s3_bucket" "crypto_bronze" {
    bucket = "lakehouse-crypto-bronze-gclauar"

    tags = {
        Ambiente = "Crypto-pipeline"
        Camada = "Bronze"
    }
}

#CRIANDO CAMADA SILVER NO S3
resource "aws_s3_bucket" "crypto_silver" {
    bucket = "lakehouse-crypto-silver-gclauar"

    tags = {
        Ambiente = "Crypto-pipeline"
        Camada = "Silver"
    }
}

#CRIANDO CAMADA GOLD NO S3
resource "aws_s3_bucket" "crypto_gold" {
    bucket = "lakehouse-crypto-gold-gclauar"

    tags = {
        Ambiente = "Crypto-pipeline"
        Camada = "Gold"
    }
}

#BLOQUEANDO ACESSO PUBLICO BRONZE
resource "aws_s3_bucket_public_access_block" "block_bronze" {
    bucket = aws_s3_bucket.crypto_bronze.id

    block_public_acls       = true
    block_public_policy     = true
    ignore_public_acls      = true
    restrict_public_buckets = true
}

#BLOQUEANDO ACESSO PUBLICO SILVER
resource "aws_s3_bucket_public_access_block" "block_silver" {
    bucket = aws_s3_bucket.crypto_silver.id

    block_public_acls       = true
    block_public_policy     = true
    ignore_public_acls      = true
    restrict_public_buckets = true
}

#BLOQUEANDO ACESSO PUBLICO GOLD
resource "aws_s3_bucket_public_access_block" "block_gold" {
    bucket = aws_s3_bucket.crypto_gold.id

    block_public_acls       = true
    block_public_policy     = true
    ignore_public_acls      = true
    restrict_public_buckets = true
}

#CRIANDO A ROLE NO IAM
resource "aws_iam_role" "lambda_crypto_role" {
  name = "role-lambda-crypto-pipeline-gclauar"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action = "sts:AssumeRole"
        Effect = "Allow"
        Principal = {
          Service = "lambda.amazonaws.com"
        }
      }
    ]
  })
}

resource "aws_iam_role_policy_attachment" "lambda_s3_access" {
  role       = aws_iam_role.lambda_crypto_role.name
  policy_arn = "arn:aws:iam::aws:policy/AmazonS3FullAccess"
}

resource "aws_iam_role_policy_attachment" "lambda_basic_execution" {
  role       = aws_iam_role.lambda_crypto_role.name
  policy_arn = "arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole"
}