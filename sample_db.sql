CREATE DATABASE flask_poc;

USE flask_poc;

CREATE TABLE users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100),
    email VARCHAR(150),
    city VARCHAR(100)
);

INSERT INTO users (name, email, city) VALUES
('Rahul Sharma', 'rahul@gmail.com', 'Pune'),
('Amit Patil', 'amit@gmail.com', 'Mumbai'),
('Sneha Joshi', 'sneha@gmail.com', 'Delhi');