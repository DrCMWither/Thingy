primes :: [Integer]
primes = 2 : filter isPrime [3,5..]
    where isPrime n = all (\p -> n `mod` p /= 0) (takeWhile (<= (floor . sqrt $ fromIntegral n)) primes)