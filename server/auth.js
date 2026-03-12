const express = require('express');
const router = express.Router();

// Basic auth middleware
function authenticate(req, res, next) {
    const token = req.headers['authorization'];
    if (!token) return res.status(401).json({ error: 'Unauthorized' });
    next();
}

// Login route
router.post('/login', (req, res) => {
    const { username, password } = req.body;
    if (username === 'admin' && password === 'secret') {
        res.json({ token: 'fake-jwt-token' });
    } else {
        res.status(401).json({ error: 'Invalid credentials' });
    }
});

module.exports = router;
