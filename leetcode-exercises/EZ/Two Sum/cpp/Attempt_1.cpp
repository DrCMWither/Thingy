/*
    Status: Accepted
    Time:   7    ms
    Mem:    14.5 MB
    TimC:   O(n)
    MemC:   O(n)
*/

#include <vector>
#include <unordered_map>

class Solution {
public:
    std::vector<int> twoSum(std::vector<int>& nums, int target) {
        std::unordered_map<int, int> index;
        for (int i = 0; i <= nums.size() - 1; i++) {
            int couple = target - nums[i];
            if (index.count(couple)) {
                return {index[couple], i};
            }
            index[nums[i]] = i;
        }
        return {}; 
    }
};
