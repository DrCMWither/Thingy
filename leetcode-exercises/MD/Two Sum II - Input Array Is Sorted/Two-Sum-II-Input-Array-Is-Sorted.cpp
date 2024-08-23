/*
    Status: Accepted
    Time:   2    ms
    Mem:    18.1 MB
    TimC:   O(n)
    MemC:   O(1)
*/

#include <vector>

class Solution {
public:
    std::vector<int> twoSum(std::vvector<int>& numbers, int target) {
        int cou = 0, ple = numbers.size() - 1;
        while (cou < ple) {
            int couple = numbers[cou] + numbers[ple];
            if (couple == target) {
                return {cou + 1, ple + 1};
            } else if (couple < target) {
                cou++;
            } else {
                ple--;
            }
        }
        return {};
    }
};