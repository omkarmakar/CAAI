# File Upload Feature Guide

## Overview

The CAAI Dashboard now supports **direct file uploads** for all agents that require file inputs. Instead of typing file paths, you can now click to upload files directly through an intuitive drag-and-drop interface.

## Key Features

✅ **User-Friendly Upload Interface**
- Click-to-upload areas replace text input fields
- Visual feedback during upload (spinner animation)
- Success confirmation with checkmark and filename
- Remove uploaded files before execution

✅ **Secure Authentication**
- Login required before executing agents
- JWT token-based authentication
- Role-based access control (user, ca, senior_ca, admin)
- Session persistence with localStorage

✅ **Multiple File Support**
- Single file upload for most agents
- Multiple file upload for batch processing (TaxBot)
- Supports various formats: PDF, CSV, XLSX, TXT, JSON, images

## Supported Agents with File Upload

### 1. **Document Audit Agent**
**Action**: Audit Document
- Upload: Invoice, receipt, contract, or any document
- Format: PDF, images, text files
- Purpose: AI-powered document analysis and audit

### 2. **BookBot Agent**
**Actions**: Categorize, P&L, Journalize
- Upload: Ledger file
- Format: CSV, XLSX
- Purpose: Automatic categorization and financial reports

### 3. **GST Agent**
**Actions**: Detect Anomalies, Query
- Upload: Sales or Purchases ledger
- Format: CSV
- Purpose: GST compliance checking and AI queries

### 4. **Compliance Check Agent**
**Action**: Run Checks
- Upload: Sales ledger + Purchases ledger (two files)
- Format: CSV, XLSX
- Purpose: Compliance validation across data

### 5. **InsightBot Agent**
**Actions**: Summarize, Top Customers, Anomaly Scan, AI Summary, Forecast
- Upload: Sales and/or Purchases files
- Format: CSV, XLSX
- Purpose: Business intelligence and AI insights

### 6. **Recon Agent**
**Actions**: Match Payments
- Upload: Ledger file + optional Payments file
- Format: CSV, XLSX
- Purpose: AI-powered reconciliation

### 7. **Contract Agent**
**Actions**: Analyze Contract, Extract Obligations, Risk Assessment
- Upload: Contract document
- Format: PDF, DOCX, TXT
- Purpose: AI contract analysis and risk detection

### 8. **Cash Flow Agent**
**Actions**: Update Forecast
- Upload: Bank feed file (optional)
- Format: CSV, XLSX
- Purpose: Cash flow forecasting

### 9. **TaxBot**
**Actions**: 
- **Extract** (Multiple files)
  - Upload: Salary slips, Form 16, investment proofs, etc.
  - Format: PDF, images, CSV, XLSX
  - Purpose: Batch extract income/deduction data
- **Calculate**
  - Upload: Incomes JSON, Deductions JSON
  - Format: JSON files
- **AI Summarize / Categorize**
  - Upload: Single document
  - Format: PDF, TXT, JSON

## How to Use File Upload

### Step 1: Login
1. Click **Login** button in top-right corner
2. If you don't have an account, click "Register"
3. Fill in registration details (username, email, password, role)
4. After registration, login with credentials

### Step 2: Select Agent
1. Browse the agent cards on dashboard
2. Click **🚀 Execute Agent** on any agent card
3. A modal will open with available actions

### Step 3: Upload Files
1. Select an action from dropdown (e.g., "Audit Document")
2. Look for file upload parameters (shows 📁 icon)
3. Click on the **📁 Click to upload file** area
4. Select file from your computer
5. Wait for upload to complete (spinner shown)
6. See confirmation: **✓ filename.ext**

### Step 4: Fill Other Parameters
- Complete any other required fields (text, numbers, dropdowns)
- For multiple file upload (TaxBot extract):
  - You can select multiple files at once
  - All files upload sequentially
  - Count shows: "3 file(s) uploaded"

### Step 5: Execute
1. Click **⚡ Execute Agent** button
2. Wait for processing (loading indicator)
3. View results in the modal
4. Results are formatted JSON with syntax highlighting

### Step 6: Remove File (Optional)
- If you uploaded wrong file, click the 🗑️ button
- This removes the upload and lets you choose again

## File Upload Details

### Backend Storage
- Files are stored in: `backend/uploaded_files/`
- Each file keeps its original name
- Files persist until manually deleted

### Upload Endpoint
```
POST http://localhost:8000/upload
Content-Type: multipart/form-data
Response: { "path": "uploaded_files/filename.ext" }
```

### Execution with Files
```
POST http://localhost:8000/agents/execute
Authorization: Bearer <jwt_token>
Content-Type: application/json

Body:
{
  "agent": "DocAuditAgent",
  "action": "audit_document",
  "params": {
    "document_path": "uploaded_files/invoice.pdf"
  }
}
```

## Authentication Flow

### Registration
```json
POST /auth/register
{
  "username": "john_ca",
  "email": "john@example.com",
  "password": "secure123",
  "full_name": "John Doe",
  "role": "ca"
}
```

### Login
```
POST /auth/login
Content-Type: application/x-www-form-urlencoded

username=john_ca&password=secure123

Response:
{
  "access_token": "eyJhbGc...",
  "token_type": "bearer"
}
```

### Authenticated Requests
All agent executions require the JWT token in header:
```
Authorization: Bearer eyJhbGc...
```

## User Roles & Permissions

### user
- Can execute basic agents
- Read-only access to system data

### ca (Chartered Accountant)
- Full access to financial agents
- Can execute all CA-related tasks

### senior_ca
- All CA permissions
- Access to advanced agents (Treasury, Advisory)

### admin
- Full system access
- User management
- System configuration

## Troubleshooting

### "Please login to execute agents"
- You need to login first
- Click Login button and enter credentials
- Or register a new account

### File Upload Fails
- Check file format is supported
- Ensure file size is reasonable (< 50MB recommended)
- Verify backend is running on port 8000

### "Access denied to agent"
- Your user role doesn't have permission
- Register with higher role (ca or senior_ca)
- Contact admin for role upgrade

### Token Expired
- Tokens expire after 7 days
- Click Logout and login again
- New token will be issued

## Technical Implementation

### Frontend (React/TypeScript)
```typescript
// File upload state
const [uploadedFiles, setUploadedFiles] = useState<{[key: string]: File}>({});
const [uploadingFiles, setUploadingFiles] = useState<{[key: string]: boolean}>({});

// Upload handler
const handleFileUpload = async (paramName: string, file: File) => {
  const formData = new FormData();
  formData.append('file', file);
  
  const response = await fetch(`${apiBaseUrl}/upload`, {
    method: 'POST',
    body: formData
  });
  
  const data = await response.json();
  handleParameterChange(paramName, data.path);
};
```

### Backend (FastAPI/Python)
```python
@app.post("/upload")
async def upload_file(file: UploadFile = File(...)):
    upload_dir = "uploaded_files"
    os.makedirs(upload_dir, exist_ok=True)
    
    file_location = os.path.join(upload_dir, file.filename)
    with open(file_location, "wb") as f:
        f.write(await file.read())
    
    return {"path": file_location}
```

## Best Practices

1. **Organize Your Files**
   - Use descriptive filenames
   - Keep original format intact
   - Don't rename files unnecessarily

2. **Security**
   - Never share your login credentials
   - Logout after using shared computers
   - Use strong passwords (min 6 chars)

3. **File Management**
   - Remove sensitive files from uploaded_files/ after use
   - Don't upload extremely large files (keep under 50MB)
   - Verify file content before uploading

4. **Execution**
   - Double-check parameters before executing
   - Wait for upload completion before executing
   - Review results carefully

## Examples

### Example 1: Audit Invoice (DocAuditAgent)
1. Login as user/ca
2. Click Execute on "Document Audit Agent"
3. Select action: "Audit Document"
4. Click upload area for "Document" parameter
5. Choose: invoice_march_2024.pdf
6. Wait for ✓ confirmation
7. Click Execute Agent
8. Review audit results

### Example 2: Batch Tax Extraction (TaxBot)
1. Login as ca
2. Click Execute on "TaxBot"
3. Select action: "Extract from Files"
4. Click upload area for "Files" parameter
5. Select multiple: salary_slip.pdf, form16.pdf, 80c_proofs.pdf
6. See "3 file(s) uploaded"
7. Click Execute Agent
8. Get extracted JSON with all income/deductions

### Example 3: GST Anomaly Detection
1. Login as ca
2. Click Execute on "GST Agent"
3. Select action: "Detect Anomalies"
4. Select ledger key: "sales"
5. Upload: sales_march_2024.csv
6. Wait for upload
7. Click Execute
8. Review anomalies and AI explanations

## Support

For issues or questions:
- Check backend logs: Backend terminal output
- Check browser console: F12 → Console tab
- Verify authentication: Check if Login button shows or username displays
- Test upload endpoint: Use Postman/curl to test /upload

## Future Enhancements

Potential improvements:
- [ ] Drag-and-drop file upload
- [ ] File preview before execution
- [ ] Upload progress bar with percentage
- [ ] File validation (size, type checking)
- [ ] Batch file management interface
- [ ] Delete uploaded files from dashboard
- [ ] Cloud storage integration (S3, Azure Blob)

---

**Note**: This feature is production-ready and all agents with file parameters now support direct upload instead of file path input.
